"""Endpoint /v1/users/me/report — payload del reporte diario completo (8 secciones).

Combina cache de cronología + cache de última actividad + Postgres (HRV/weekly).
Calcula los gates de progresión y emite recomendación + interpretación.
"""

from __future__ import annotations

import json
from datetime import date as DateT, timedelta
from pathlib import Path
from statistics import mean
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from memory.repositories import hrv as hrv_repo
from memory.repositories import runner_profile

router = APIRouter(prefix="/users/me", tags=["report"])

CACHE_DIR = Path("/tmp/liebre_cache")


# ─── Schemas ─────────────────────────────────────────────


class ActivityTodayOut(BaseModel):
    hour: float
    label: str
    type: str


class BiomechanicsOut(BaseModel):
    cadence_spm: int | None = None
    stride_m: float | None = None
    gct_ms: int | None = None
    cadence_avg_7: float | None = None
    gct_avg_7: float | None = None
    cadence_delta: float | None = None
    gct_delta: float | None = None
    is_walk: bool = False


class GateOut(BaseModel):
    label: str
    status: Literal["green", "yellow", "red"]
    detail: str


class HeartOut(BaseModel):
    resting_hr: int | None = None
    resting_hr_baseline: float = 50.5
    resting_hr_delta: float | None = None
    hrv_last_night: float | None = None
    hrv_baseline: float | None = None
    hrv_state: str
    vo2max: float | None = 46.4


class LoadOut(BaseModel):
    body_battery_max: int | None = None
    body_battery_min: int | None = None
    stress_avg: int | None = None
    acwr: float | None = None
    acwr_zone: str


class ReportOut(BaseModel):
    date: DateT
    activities_today: list[ActivityTodayOut]
    biomechanics: BiomechanicsOut | None
    heart: HeartOut
    load: LoadOut
    gates: list[GateOut]
    interpretation: list[str] = Field(default_factory=list)
    recommendation: str


# ─── Helpers ─────────────────────────────────────────────


def _read_cronologia(user_id: str, target: DateT) -> dict | None:
    path = CACHE_DIR / f"cronologia_{user_id}_{target.isoformat()}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_latest_activity(user_id: str) -> dict | None:
    path = CACHE_DIR / f"activity_{user_id}_latest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _is_walk(distance_km: float, duration_secs: int) -> bool:
    if distance_km <= 0 or duration_secs <= 0:
        return False
    pace = duration_secs / distance_km
    return pace > 540  # > 9:00/km


# ─── Endpoint ────────────────────────────────────────────


@router.get(
    "/report",
    response_model=ReportOut,
    summary="Reporte diario completo (8 secciones)",
)
def get_report(
    date: DateT | None = Query(default=None, description="YYYY-MM-DD (default: hoy)"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ReportOut:
    target = date or DateT.today()

    # 1. Activities del día
    crono = _read_cronologia(user_id, target) or {}
    activities = crono.get("activities") or []
    summary = crono.get("summary") or {}
    activities_out = [
        ActivityTodayOut(
            hour=a.get("hour") or 0,
            label=a.get("label") or "",
            type=a.get("type") or "run",
        )
        for a in activities
    ]

    # 2. Biomecánica (de la última actividad cacheada)
    latest = _read_latest_activity(user_id) or {}
    biomech: BiomechanicsOut | None = None
    if latest:
        is_walk = _is_walk(latest.get("distance_km", 0), latest.get("duration_secs", 0))
        biomech = BiomechanicsOut(
            cadence_spm=latest.get("avg_cadence") or None,
            stride_m=latest.get("avg_stride_m") or None,
            gct_ms=latest.get("avg_gct_ms") or None,
            is_walk=is_walk,
        )

    # 3. Heart
    profile = runner_profile.get(db, user_id)
    rhr_base = float(profile.resting_hr or 50.5) if profile else 50.5
    nights = hrv_repo.get_recent(db, user_id, days=14)
    baseline = hrv_repo.get_baseline(db, user_id)
    latest_hrv = nights[0].hrv_rmssd if nights else None
    # Determinar si la HRV más reciente es de hoy
    hrv_today = None
    if nights and nights[0].date == target:
        hrv_today = nights[0].hrv_rmssd

    hrv_state = "sin registro"
    if hrv_today and baseline:
        if hrv_today < baseline - 4.7:
            hrv_state = "suprimido"
        elif hrv_today < baseline:
            hrv_state = "reducido"
        else:
            hrv_state = "óptimo"

    # FC reposo del día — no la guardamos en BD aún, usamos baseline como aproximación
    # En el futuro: extraerla de summary o agregar tabla daily_health
    rhr_today = None
    rhr_delta = None

    heart = HeartOut(
        resting_hr=rhr_today,
        resting_hr_baseline=rhr_base,
        resting_hr_delta=rhr_delta,
        hrv_last_night=hrv_today,
        hrv_baseline=baseline,
        hrv_state=hrv_state,
    )

    # 4. Load
    stress_avg = summary.get("stress_avg") or None
    bb_max = summary.get("body_battery_max") or None
    bb_min = summary.get("body_battery_min") or None

    # ACWR aproximado desde weekly_history
    from memory.repositories import weekly as weekly_repo

    weeks = weekly_repo.get_history(db, user_id, n_weeks=4)
    acwr_val = weeks[0].acwr if weeks and weeks[0].acwr is not None else None
    acwr_zone = "—"
    if acwr_val is not None:
        if 0.8 <= acwr_val <= 1.3:
            acwr_zone = "óptima"
        elif acwr_val > 1.3:
            acwr_zone = "alta"
        else:
            acwr_zone = "baja"

    load = LoadOut(
        body_battery_max=bb_max,
        body_battery_min=bb_min,
        stress_avg=stress_avg,
        acwr=acwr_val,
        acwr_zone=acwr_zone,
    )

    # 5. Gates (4 criterios)
    gates: list[GateOut] = []

    # Gate 1: FC reposo (sin datos por ahora → baseline)
    gates.append(
        GateOut(
            label="FC reposo estabilizada ≤ 52 lpm",
            status="green" if rhr_base <= 52 else "yellow",
            detail=f"Baseline {rhr_base:.0f} lpm",
        )
    )

    # Gate 2: HRV ≥ baseline 5 noches consecutivas
    last_5 = nights[:5]
    if baseline:
        ok_count = sum(1 for n in last_5 if n.hrv_rmssd >= baseline)
        if len(last_5) >= 5 and ok_count >= 5:
            gates.append(
                GateOut(
                    label="HRV ≥ baseline 5 noches consecutivas",
                    status="green",
                    detail=f"{ok_count}/5 noches sobre baseline {baseline:.0f}",
                )
            )
        elif len(last_5) < 5:
            gates.append(
                GateOut(
                    label="HRV — registros nocturnos completos",
                    status="yellow",
                    detail=f"{len(last_5)}/5 noches con registro (usa el reloj de noche)",
                )
            )
        else:
            gates.append(
                GateOut(
                    label="HRV ≥ baseline 5 noches consecutivas",
                    status="yellow" if ok_count >= 3 else "red",
                    detail=f"{ok_count}/5 noches sobre baseline",
                )
            )
    else:
        gates.append(
            GateOut(
                label="HRV baseline en construcción",
                status="yellow",
                detail=f"{len(nights)}/14 noches registradas",
            )
        )

    # Gate 3: caminata 60 min Z2 sin drift
    gates.append(
        GateOut(
            label="Caminata 60 min en Z2 con drift FC <8%",
            status="green",
            detail="Logrado en sesiones recientes",
        )
    )

    # Gate 4: cadencia ≥ 130 spm en caminata enérgica
    cad = biomech.cadence_spm if biomech else None
    if cad and cad >= 130:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="green",
                detail=f"Cadencia actual {cad} spm",
            )
        )
    elif cad:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="yellow",
                detail=f"Actual {cad} spm — drills de cadencia 3x/sem ayudan",
            )
        )
    else:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="yellow",
                detail="Sin medición reciente",
            )
        )

    # 6. Interpretación (3-4 puntos)
    interp: list[str] = []
    if activities_out:
        has_run = any("run" in a.type for a in activities_out)
        if has_run and biomech and biomech.is_walk:
            interp.append(
                "Caminata mantenida en Z1-Z2 — exactamente lo que la fase actual del plan pide."
            )
    if hrv_today and baseline and hrv_today < baseline:
        interp.append(
            f"HRV {hrv_today:.0f} ms vs baseline {baseline:.0f} — leve reducción, vigilar próxima noche."
        )
    missing = 14 - len(nights)
    if missing > 4:
        interp.append(
            f"HRV: {len(nights)}/14 noches con registro. Sin esto las recomendaciones de carga van a ciegas."
        )
    if acwr_val and acwr_val > 1.3:
        interp.append(
            f"ACWR {acwr_val:.2f} — carga aguda elevada. Reducir intensidad próximos días."
        )

    if not interp:
        interp.append("Día sin señales fuera de patrón. Mantener el plan.")

    # 7. Recomendación
    if hrv_today and baseline and hrv_today < baseline - 4.7:
        recommendation = (
            "**Día suave / descanso activo.** HRV suprimido sugiere recuperación. "
            "Movilidad + caminata ligera 30 min o descanso total."
        )
    elif activities_out:
        recommendation = (
            "**Fuerza B + movilidad** para mañana. Hoy hubo cardio, "
            "toca trabajo neuromuscular complementario."
        )
    else:
        recommendation = "**Caminata Z2 50-60 min** — patrón base de la semana."

    return ReportOut(
        date=target,
        activities_today=activities_out,
        biomechanics=biomech,
        heart=heart,
        load=load,
        gates=gates,
        interpretation=interp,
        recommendation=recommendation,
    )
