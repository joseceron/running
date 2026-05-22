"""Operaciones sobre `weekly_history`."""

from __future__ import annotations

from datetime import date as DateT

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from memory.models import WeeklyHistory


def upsert(
    session: Session,
    user_id: str,
    *,
    week_start: DateT,
    plan_km: float | None = None,
    executed_km: float | None = None,
    avg_hrv: float | None = None,
    avg_body_battery: float | None = None,
    acwr: float | None = None,
    agent_notes: str | None = None,
) -> None:
    stmt = (
        pg_insert(WeeklyHistory)
        .values(
            user_id=user_id,
            week_start=week_start,
            plan_km=plan_km,
            executed_km=executed_km,
            avg_hrv=avg_hrv,
            avg_body_battery=avg_body_battery,
            acwr=acwr,
            agent_notes=agent_notes,
        )
        .on_conflict_do_update(
            constraint="uq_weekly_user_week",
            set_={
                "plan_km": plan_km,
                "executed_km": executed_km,
                "avg_hrv": avg_hrv,
                "avg_body_battery": avg_body_battery,
                "acwr": acwr,
                "agent_notes": agent_notes,
            },
        )
    )
    session.execute(stmt)


def get_history(session: Session, user_id: str, n_weeks: int = 4) -> list[WeeklyHistory]:
    stmt = (
        select(WeeklyHistory)
        .where(WeeklyHistory.user_id == user_id)
        .order_by(WeeklyHistory.week_start.desc())
        .limit(n_weeks)
    )
    return list(session.scalars(stmt).all())
