"""Operaciones sobre `hrv_log`."""

from __future__ import annotations

from datetime import date as DateT

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from memory.models import HRVLog

BASELINE_DAYS_REQUIRED = 14
BASELINE_AVG_WINDOW = 7


def log(session: Session, user_id: str, hrv_date: DateT, hrv_rmssd: float) -> None:
    """Upsert idempotente del HRV de una fecha para un usuario."""
    stmt = (
        pg_insert(HRVLog)
        .values(user_id=user_id, date=hrv_date, hrv_rmssd=hrv_rmssd)
        .on_conflict_do_update(
            constraint="uq_hrv_user_date",
            set_={"hrv_rmssd": hrv_rmssd},
        )
    )
    session.execute(stmt)


def get_recent(session: Session, user_id: str, days: int = 14) -> list[HRVLog]:
    stmt = (
        select(HRVLog)
        .where(HRVLog.user_id == user_id)
        .order_by(HRVLog.date.desc())
        .limit(days)
    )
    return list(session.scalars(stmt).all())


def get_baseline(session: Session, user_id: str) -> float | None:
    """Media móvil de los últimos `BASELINE_AVG_WINDOW` días sobre los últimos
    `BASELINE_DAYS_REQUIRED` registros. Retorna None si hay menos de 14 días."""
    rows = get_recent(session, user_id, days=BASELINE_DAYS_REQUIRED)
    if len(rows) < BASELINE_DAYS_REQUIRED:
        return None
    values = [r.hrv_rmssd for r in rows[:BASELINE_AVG_WINDOW]]
    return sum(values) / len(values)


def get_baseline_progress(session: Session, user_id: str) -> tuple[int, int]:
    """Retorna (días registrados, días requeridos). Útil para UI de onboarding."""
    rows = get_recent(session, user_id, days=BASELINE_DAYS_REQUIRED)
    return len(rows), BASELINE_DAYS_REQUIRED
