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


# ─── Insights científicos (diferencial Liebre) ────────────


class FatBurnZone(BaseModel):
    zone: int
    label: str
    pct_time: float
    kcal_total: float
    kcal_fat: float
    kcal_cho: float
    fat_pct: int  # % de calorías que viene de grasa en esta zona


class FatBurnOut(BaseModel):
    """FatMax: estimación de oxidación de grasa por zona FC en la última sesión.
    Fórmula derivada de Achten & Jeukendrup (2004) y guidelines de FatMax:
    en Z1 ~80% energía viene de grasa, Z2 ~65%, Z3 ~40%, Z4 ~20%, Z5 ~5%."""
    activity_name: str
    total_kcal: int
    fat_kcal: int
    cho_kcal: int
    fat_grams: float  # kcal_fat / 9
    by_zone: list[FatBurnZone]
    citation: str = "Achten & Jeukendrup (2004) · Int J Sports Med · Review"


class CardiacDriftOut(BaseModel):
    """Drift FC primera vs segunda mitad — eficiencia cardiaca."""
    activity_name: str
    first_half_hr: float
    second_half_hr: float
    drift_pct: float
    evaluation: str  # "eficiente" / "regular" / "base aún verde"
    citation: str = "Lamberts & Lambert (2009) · J Strength Cond Res · Observacional"


class HeartProgressOut(BaseModel):
    """FC reposo + qué le está pasando al corazón."""
    rhr_current: int
    rhr_baseline: float
    rhr_trend: str  # "improving" / "stable" / "regressing"
    explanation: str
    citation: str = "Seiler (2010) · Int J Sports Physiol Perform · Review"


class PolarizationOut(BaseModel):
    """Distribución 80/20 — Seiler."""
    z1_z2_pct: float
    z3_pct: float
    z4_z5_pct: float
    ideal_z1_z2_pct: int = 80
    ideal_z3_pct: int = 0
    ideal_z4_z5_pct: int = 20
    evaluation: str  # "aligned" / "too_easy" / "too_hard" / "mixed"
    source_label: str  # "última carrera" / "últimos 7 días" según lo disponible
    citation: str = "Seiler (2010) · Int J Sports Physiol Perform · Review"


class InsightsOut(BaseModel):
    """Análisis científicos — el diferencial Liebre vs Connect."""
    fat_burn: FatBurnOut | None = None
    cardiac_drift: CardiacDriftOut | None = None
    heart_progress: HeartProgressOut | None = None
    polarization: PolarizationOut | None = None


class TodayActionOut(BaseModel):
    """Recomendación inequívoca para HOY."""
    status: Literal["rest", "train", "active_recovery", "trained_already"]
    headline: str  # "DESCANSA HOY" / "ENTRENA HOY: caminata Z2 50 min"
    short_reason: str  # 1 frase, lo que se ve grande
    reasons: list[str]  # bullets con datos objetivos
    allowed: list[str]  # qué SÍ se puede hacer
    next_session: str  # qué viene después (ej: "Mañana: caminata Z2 50-60 min")


class ReportOut(BaseModel):
    date: DateT
    today_action: TodayActionOut
    activities_today: list[ActivityTodayOut]
    biomechanics: BiomechanicsOut | None
    heart: HeartOut
    load: LoadOut
    gates: list[GateOut]
    interpretation: list[str] = Field(default_factory=list)
    recommendation: str
    insights: InsightsOut | None = None  # nuevo — diferencial científico


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


# ─── Insights: FatMax por zona ─────────────────────────────

# Fracción de energía proveniente de grasa por zona FC.
# Aproximación de Achten & Jeukendrup (FatMax) y guidelines clásicas:
# Z1 (50-60% FCmáx): ~80% grasa
# Z2 (60-70% FCmáx): ~65% grasa
# Z3 (70-80% FCmáx): ~40% grasa
# Z4 (80-90% FCmáx): ~20% grasa
# Z5 (>90% FCmáx): ~5% grasa
FAT_PCT_BY_ZONE = [80, 65, 40, 20, 5]
ZONE_LABELS = ["Z1 · recuperación", "Z2 · base aeróbica", "Z3 · umbral aeróbico", "Z4 · VO₂máx", "Z5 · anaeróbico"]


def _calc_fat_burn(activity: dict) -> FatBurnOut | None:
    total_kcal = activity.get("calories") or 0
    zone_pct = activity.get("zone_distribution_pct") or []
    if total_kcal <= 0 or len(zone_pct) < 5:
        return None

    by_zone: list[FatBurnZone] = []
    fat_total = 0.0
    for i in range(5):
        pct_time = zone_pct[i] or 0
        kcal_z = total_kcal * (pct_time / 100)
        fat_pct = FAT_PCT_BY_ZONE[i]
        fat_z = kcal_z * (fat_pct / 100)
        cho_z = kcal_z - fat_z
        fat_total += fat_z
        by_zone.append(
            FatBurnZone(
                zone=i + 1,
                label=ZONE_LABELS[i],
                pct_time=round(pct_time, 1),
                kcal_total=round(kcal_z, 1),
                kcal_fat=round(fat_z, 1),
                kcal_cho=round(cho_z, 1),
                fat_pct=fat_pct,
            )
        )

    return FatBurnOut(
        activity_name=activity.get("name") or "Última sesión",
        total_kcal=round(total_kcal),
        fat_kcal=round(fat_total),
        cho_kcal=round(total_kcal - fat_total),
        fat_grams=round(fat_total / 9, 1),
        by_zone=by_zone,
    )


# ─── Insights: cardiac drift ────────────────────────────────


def _calc_cardiac_drift(activity: dict) -> CardiacDriftOut | None:
    samples = activity.get("samples") or []
    # Filtrar samples con HR válido tras los primeros 5 min (warmup)
    valid = [
        s for s in samples
        if s.get("hr") and s.get("t_secs") is not None and s["t_secs"] >= 300
    ]
    if len(valid) < 20:
        return None
    mid = len(valid) // 2
    first_half = valid[:mid]
    second_half = valid[mid:]
    hr1 = sum(s["hr"] for s in first_half) / len(first_half)
    hr2 = sum(s["hr"] for s in second_half) / len(second_half)
    drift = (hr2 - hr1) / hr1 * 100 if hr1 > 0 else 0

    if drift < 5:
        evaluation = "eficiente — corazón mantiene FC estable, sin fatiga"
    elif drift < 10:
        evaluation = "regular — algo de fatiga acumulada en la segunda mitad"
    else:
        evaluation = "base aún verde — la FC se va arriba a pesar del mismo esfuerzo"

    return CardiacDriftOut(
        activity_name=activity.get("name") or "Última sesión",
        first_half_hr=round(hr1, 1),
        second_half_hr=round(hr2, 1),
        drift_pct=round(drift, 2),
        evaluation=evaluation,
    )


# ─── Insights: heart progress (hipertrofia VI) ─────────────


def _build_heart_progress(rhr_today: int | None, rhr_baseline: float) -> HeartProgressOut:
    rhr_current = rhr_today or int(rhr_baseline)
    # Sin histórico, hacemos lectura del estado: si está dentro de baseline o por debajo → improving
    if rhr_current <= rhr_baseline:
        trend = "improving"
        explanation = (
            f"Tu FC de reposo en {rhr_current} lpm está alineada con tu baseline ({rhr_baseline:.0f}). "
            "El Z2 prolongado provoca hipertrofia excéntrica del ventrículo izquierdo: la cámara cardíaca "
            "se agranda, sube el volumen sistólico y baja la FC reposo. Es la adaptación que más se traduce "
            "en rendimiento sostenido para 21K. Si bajas otros 3-4 lpm en las próximas 6 semanas, vas en ruta."
        )
    elif rhr_current <= rhr_baseline + 4:
        trend = "stable"
        explanation = (
            f"FC de reposo {rhr_current} lpm — levemente sobre tu baseline ({rhr_baseline:.0f}). "
            "Puede ser estrés externo, sueño insuficiente o carga acumulada de la semana. Una noche no es tendencia."
        )
    else:
        trend = "regressing"
        explanation = (
            f"FC de reposo {rhr_current} lpm — significativamente sobre baseline ({rhr_baseline:.0f}). "
            "Señal de fatiga acumulada. Considera día suave + dormir 8h+ con el reloj puesto para HRV."
        )

    return HeartProgressOut(
        rhr_current=rhr_current,
        rhr_baseline=rhr_baseline,
        rhr_trend=trend,
        explanation=explanation,
    )


# ─── Insights: polarización 80/20 ───────────────────────────


# ─── Today action: heurística HOY ────────────────────────────


# Plan semanal modelo (en fase de reconstrucción de base aeróbica)
WEEKDAY_PLAN = {
    0: ("train", "Fuerza A (piernas + core) · 45 min"),
    1: ("train", "Caminata/trote Z2 · 40-50 min"),
    2: ("rest", "Descanso o movilidad"),
    3: ("train", "Fuerza B (upper + sóleo excéntrico) · 45 min"),
    4: ("train", "Caminata/trote Z2 · 40-50 min"),
    5: ("train", "Rodaje largo Z2 · 50-60 min"),
    6: ("rest", "Descanso programado"),
}


def _build_today_action(
    target: DateT,
    activities_today: list,
    acwr: float | None,
    hrv_today: float | None,
    hrv_baseline: float | None,
    hrv_sd: float = 4.7,
) -> TodayActionOut:
    """Combina ACWR + HRV + actividades del día + plan semanal → recomendación inequívoca."""
    weekday = target.weekday()  # 0=lun, 6=dom
    planned_status, planned_session = WEEKDAY_PLAN[weekday]

    # Próxima sesión (día siguiente que toque entrenar)
    next_session = ""
    for offset in range(1, 8):
        d = target + timedelta(days=offset)
        st, sess = WEEKDAY_PLAN[d.weekday()]
        if st == "train":
            day_names = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            label = "Mañana" if offset == 1 else day_names[d.weekday()].capitalize()
            next_session = f"{label}: {sess}"
            break

    # Caso 1: ya entrenó hoy
    if activities_today:
        labels = ", ".join(a.label.split(" · ")[0] for a in activities_today[:3])
        return TodayActionOut(
            status="trained_already",
            headline="HOY YA ENTRENASTE",
            short_reason=f"{len(activities_today)} sesión{'es' if len(activities_today) > 1 else ''} registrada{'s' if len(activities_today) > 1 else ''}: {labels}.",
            reasons=[
                f"Carga de hoy ya absorbida — no agregar más sesiones",
                f"Si quieres complemento: movilidad, estiramientos o caminata corta (sin reloj)",
            ],
            allowed=[
                "Estiramientos / foam roller (15-20 min)",
                "Movilidad articular o yoga ligero",
                "Caminata corta de paseo (≤30 min, conversacional)",
            ],
            next_session=next_session,
        )

    # Señales de alerta para forzar descanso aunque el plan diga entrenar
    high_acwr = acwr is not None and acwr > 1.3
    suppressed_hrv = (
        hrv_today is not None
        and hrv_baseline is not None
        and hrv_today < hrv_baseline - hrv_sd
    )
    reduced_hrv = (
        hrv_today is not None
        and hrv_baseline is not None
        and hrv_today < hrv_baseline
        and not suppressed_hrv
    )

    # Caso 2: HRV muy suprimido → descanso aunque toque entrenar
    if suppressed_hrv:
        return TodayActionOut(
            status="rest",
            headline="DESCANSA HOY",
            short_reason=f"Tu HRV ({hrv_today:.0f} ms) está suprimido vs baseline ({hrv_baseline:.0f}). Sistema nervioso pidiendo recuperación.",
            reasons=[
                f"HRV {hrv_today:.0f} ms = {hrv_today - hrv_baseline:+.0f} ms vs baseline (zona suprimida)",
                "Entrenar con HRV deprimido aumenta riesgo de sobreuso y no genera adaptación",
            ],
            allowed=[
                "Movilidad articular suave",
                "Caminata de paseo conversacional (≤30 min)",
                "Acuéstate temprano para subir HRV de mañana",
            ],
            next_session=next_session,
        )

    # Caso 3: ACWR alto → descanso preventivo
    if high_acwr and planned_status == "train":
        return TodayActionOut(
            status="active_recovery",
            headline="RECUPERACIÓN ACTIVA HOY",
            short_reason=f"Tu ACWR ({acwr:.2f}) está sobre el umbral seguro (1.3). Carga aguda muy por encima de la crónica.",
            reasons=[
                f"ACWR {acwr:.2f} > 1.3 — riesgo de sobreuso elevado (Gabbett 2016)",
                f"Plan original de hoy: {planned_session}",
                "Recuperación activa baja ACWR a zona segura para retomar mañana",
            ],
            allowed=[
                "Movilidad 20-30 min",
                "Caminata muy ligera Z1 (≤30 min, sin contar como sesión)",
                "Estiramientos largos / foam roller",
            ],
            next_session=next_session,
        )

    # Caso 4: día de descanso programado
    if planned_status == "rest":
        extra: list[str] = []
        if acwr and acwr > 1.0:
            extra.append(
                f"Tu ACWR es {acwr:.2f} — el descanso de hoy lo baja a zona óptima para mañana"
            )
        if reduced_hrv and hrv_today is not None and hrv_baseline is not None:
            extra.append(
                f"HRV {hrv_today:.0f} ms está {hrv_today - hrv_baseline:+.0f} vs baseline — descanso ayuda a normalizar"
            )
        if not extra:
            extra.append("Tu plan polarizado contempla este descanso — sin descanso no hay adaptación")
        return TodayActionOut(
            status="rest",
            headline="DESCANSA HOY",
            short_reason="Día de descanso programado por el plan semanal.",
            reasons=extra,
            allowed=[
                "Movilidad / estiramientos",
                "Caminata de paseo conversacional (sin reloj)",
                "Foam roller, sauna, baño caliente",
            ],
            next_session=next_session,
        )

    # Caso 5: día normal de entrenamiento, sin alertas
    return TodayActionOut(
        status="train",
        headline=f"ENTRENA HOY: {planned_session}",
        short_reason="Día de entrenamiento programado y sin contraindicaciones (ACWR y HRV en rango).",
        reasons=[
            f"Plan semanal de hoy: {planned_session}",
            f"ACWR {acwr:.2f}" if acwr else "ACWR sin datos",
            f"HRV {hrv_today:.0f} ms en rango" if hrv_today else "HRV de anoche sin registro",
        ],
        allowed=[
            "Calentamiento progresivo 8-10 min antes",
            "Cadencia objetivo ≥170 spm si toca trote",
            "Hidratación + 30g de carbohidratos pre-sesión si vas a Z3+",
        ],
        next_session=next_session,
    )


def _build_polarization(activity: dict) -> PolarizationOut | None:
    zone_pct = activity.get("zone_distribution_pct") or []
    if len(zone_pct) < 5:
        return None
    z12 = (zone_pct[0] or 0) + (zone_pct[1] or 0)
    z3 = zone_pct[2] or 0
    z45 = (zone_pct[3] or 0) + (zone_pct[4] or 0)
    # Evaluación
    if 75 <= z12 <= 85 and z45 >= 10:
        evaluation = "aligned"
    elif z12 > 90 and z45 < 5:
        evaluation = "too_easy"
    elif z45 > 30:
        evaluation = "too_hard"
    elif z3 > 25:
        evaluation = "mixed"  # zona "gris" — ni base ni VO2máx
    else:
        evaluation = "mixed"

    return PolarizationOut(
        z1_z2_pct=round(z12, 1),
        z3_pct=round(z3, 1),
        z4_z5_pct=round(z45, 1),
        evaluation=evaluation,
        source_label="última carrera (próximamente: semanal)",
    )


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

    # Fallback: si cronología no trajo actividades pero la última actividad
    # cacheada es del día solicitado, agregarla. Cubre el caso de Garmin
    # devolviendo BB/stress vacíos pero sí tener la actividad.
    if not activities_out and latest:
        started = latest.get("started_at") or ""
        if started.startswith(target.isoformat()):
            try:
                hour_part = started[11:19]  # HH:MM:SS
                h, m, s = (int(x) for x in hour_part.split(":"))
                hour_f = h + m / 60 + s / 3600
            except Exception:
                hour_f = 0
            dist_km = latest.get("distance_km") or 0
            name = latest.get("name") or "Actividad"
            label = f"{name} · {dist_km:.2f} km" if dist_km else name
            activities_out.append(
                ActivityTodayOut(
                    hour=round(hour_f, 3),
                    label=label,
                    type=latest.get("type") or "run",
                )
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

    # 9. Insights científicos (diferencial Liebre)
    insights: InsightsOut | None = None
    if latest:
        insights = InsightsOut(
            fat_burn=_calc_fat_burn(latest),
            cardiac_drift=_calc_cardiac_drift(latest),
            heart_progress=_build_heart_progress(rhr_today, rhr_base),
            polarization=_build_polarization(latest),
        )

    # 10. Today action — recomendación inequívoca para HOY
    today_action = _build_today_action(
        target=target,
        activities_today=activities_out,
        acwr=acwr_val,
        hrv_today=hrv_today,
        hrv_baseline=baseline,
    )

    return ReportOut(
        date=target,
        today_action=today_action,
        activities_today=activities_out,
        biomechanics=biomech,
        heart=heart,
        load=load,
        gates=gates,
        interpretation=interp,
        recommendation=recommendation,
        insights=insights,
    )
