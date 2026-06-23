"""Endpoints de composición corporal — báscula inteligente.

POST /v1/users/me/body-composition   — registra nueva medición
GET  /v1/users/me/body-composition   — historial (últimas 52 semanas)
GET  /v1/users/me/progress           — curva de adaptación (HRV + volumen + cuerpo)
"""

from __future__ import annotations

from datetime import date as DateT
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from memory.repositories import body_composition as bc_repo, hrv as hrv_repo, weekly as weekly_repo

router = APIRouter(prefix="/users/me", tags=["body-composition"])


# ── Schemas de entrada / salida ──────────────────────────────────────────────

class BodyCompositionIn(BaseModel):
    measured_at: DateT
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    subcutaneous_fat_pct: Optional[float] = None
    visceral_fat: Optional[float] = None
    fat_free_weight_kg: Optional[float] = None
    skeletal_muscle_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    bone_mass_kg: Optional[float] = None
    body_water_pct: Optional[float] = None
    bmr_kcal: Optional[int] = None
    metabolic_age: Optional[int] = None
    protein_pct: Optional[float] = None
    notes: Optional[str] = None


class BodyCompositionOut(BaseModel):
    id: int
    measured_at: DateT
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    subcutaneous_fat_pct: Optional[float] = None
    visceral_fat: Optional[float] = None
    fat_free_weight_kg: Optional[float] = None
    skeletal_muscle_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    bone_mass_kg: Optional[float] = None
    body_water_pct: Optional[float] = None
    bmr_kcal: Optional[int] = None
    metabolic_age: Optional[int] = None
    protein_pct: Optional[float] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class BodyCompositionHistoryOut(BaseModel):
    entries: list[BodyCompositionOut]


# ── Progresión ────────────────────────────────────────────────────────────────

class HRVProgressPoint(BaseModel):
    date: DateT
    hrv_ms: float


class WeeklyProgressPoint(BaseModel):
    week_start: DateT
    executed_km: Optional[float]
    avg_hrv: Optional[float]
    acwr: Optional[float]


class BodyProgressPoint(BaseModel):
    date: DateT
    weight_kg: Optional[float]
    body_fat_pct: Optional[float]
    muscle_mass_kg: Optional[float]


class ProgressOut(BaseModel):
    hrv_nights: list[HRVProgressPoint]
    weekly: list[WeeklyProgressPoint]
    body: list[BodyProgressPoint]
    summary: dict


def _build_summary(
    hrv_nights: list,
    weeks: list,
    body_entries: list,
) -> dict:
    """Texto de 2-3 frases describiendo la tendencia de adaptación."""
    parts = []

    if len(hrv_nights) >= 4:
        first_half = [n.hrv_rmssd for n in hrv_nights[len(hrv_nights)//2:]]
        second_half = [n.hrv_rmssd for n in hrv_nights[:len(hrv_nights)//2]]
        avg_old = sum(first_half) / len(first_half)
        avg_new = sum(second_half) / len(second_half)
        delta = avg_new - avg_old
        if delta > 1.5:
            parts.append(f"HRV mejorando: +{delta:.1f} ms respecto a hace {len(hrv_nights)//2} noches — adaptación aeróbica en curso.")
        elif delta < -1.5:
            parts.append(f"HRV en ligero descenso ({delta:.1f} ms) — revisa descanso y carga acumulada.")
        else:
            parts.append("HRV estable — sistema autónomo equilibrado.")

    if len(weeks) >= 3:
        kms = [w.executed_km for w in weeks if w.executed_km]
        if kms:
            trend = kms[0] - kms[-1]  # reciente - antiguo (weeks desc)
            if trend > 3:
                parts.append(f"Volumen semanal creciendo +{trend:.1f} km vs inicio — progresión controlada.")
            elif trend < -3:
                parts.append("Volumen bajando — ¿semana de reducción o detraining?")

    if len(body_entries) >= 2:
        latest = body_entries[0]
        oldest = body_entries[-1]
        if latest.body_fat_pct and oldest.body_fat_pct:
            fat_delta = latest.body_fat_pct - oldest.body_fat_pct
            if fat_delta < -0.5:
                parts.append(f"Grasa corporal bajando {abs(fat_delta):.1f}% desde el inicio — composición mejorando.")
            elif fat_delta > 0.5:
                parts.append("Grasa corporal ligeramente al alza — revisar balance calórico.")

    if not parts:
        parts.append("Datos insuficientes para calcular tendencia. Sigue registrando semanalmente.")

    return {"narrative": " ".join(parts)}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/body-composition",
    response_model=BodyCompositionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar medición de báscula",
)
def post_body_composition(
    body: BodyCompositionIn,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> BodyCompositionOut:
    row = bc_repo.upsert(
        db,
        user_id,
        measured_at=body.measured_at,
        **body.model_dump(exclude={"measured_at"}, exclude_none=True),
    )
    return BodyCompositionOut.model_validate(row)


@router.get(
    "/body-composition",
    response_model=BodyCompositionHistoryOut,
    summary="Historial de composición corporal",
)
def get_body_composition(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> BodyCompositionHistoryOut:
    rows = bc_repo.get_history(db, user_id)
    return BodyCompositionHistoryOut(
        entries=[BodyCompositionOut.model_validate(r) for r in rows]
    )


@router.get(
    "/progress",
    response_model=ProgressOut,
    summary="Curva de adaptación: HRV + volumen + composición corporal",
)
def get_progress(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ProgressOut:
    hrv_nights = hrv_repo.get_recent(db, user_id, days=60)
    weeks = weekly_repo.get_history(db, user_id, n_weeks=12)
    body_entries = bc_repo.get_history(db, user_id, limit=26)

    return ProgressOut(
        hrv_nights=[
            HRVProgressPoint(date=n.date, hrv_ms=n.hrv_rmssd)
            for n in hrv_nights
        ],
        weekly=[
            WeeklyProgressPoint(
                week_start=w.week_start,
                executed_km=w.executed_km,
                avg_hrv=w.avg_hrv,
                acwr=w.acwr,
            )
            for w in weeks
        ],
        body=[
            BodyProgressPoint(
                date=b.measured_at,
                weight_kg=b.weight_kg,
                body_fat_pct=b.body_fat_pct,
                muscle_mass_kg=b.muscle_mass_kg,
            )
            for b in body_entries
        ],
        summary=_build_summary(hrv_nights, weeks, body_entries),
    )
