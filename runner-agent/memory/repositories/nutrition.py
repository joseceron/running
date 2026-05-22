"""Operaciones sobre `nutrition_log`."""

from __future__ import annotations

from datetime import date as DateT, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from memory.models import NutritionLog

DEFICIT_THRESHOLD_KCAL = -500
DEFICIT_CONSECUTIVE_DAYS = 3


def log_intake(
    session: Session,
    user_id: str,
    intake_date: DateT,
    *,
    kcal: float,
    protein_g: float | None = None,
) -> None:
    stmt = (
        pg_insert(NutritionLog)
        .values(user_id=user_id, date=intake_date, kcal=kcal, protein_g=protein_g)
        .on_conflict_do_update(
            constraint="uq_nutrition_user_date",
            set_={"kcal": kcal, "protein_g": protein_g},
        )
    )
    session.execute(stmt)


def get_recent(session: Session, user_id: str, days: int = 7) -> list[NutritionLog]:
    cutoff = DateT.today() - timedelta(days=days)
    stmt = (
        select(NutritionLog)
        .where(NutritionLog.user_id == user_id)
        .where(NutritionLog.date >= cutoff)
        .order_by(NutritionLog.date.desc())
    )
    return list(session.scalars(stmt).all())


def get_by_date(session: Session, user_id: str, target: DateT) -> NutritionLog | None:
    stmt = (
        select(NutritionLog)
        .where(NutritionLog.user_id == user_id)
        .where(NutritionLog.date == target)
    )
    return session.scalar(stmt)
