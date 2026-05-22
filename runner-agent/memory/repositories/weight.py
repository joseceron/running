"""Operaciones sobre `body_weight_history`."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from memory.models import BodyWeightHistory, RunnerProfile


def record(
    session: Session,
    user_id: str,
    weight_kg: float,
    *,
    recorded_at: datetime | None = None,
) -> None:
    """Inserta nuevo peso en historial y actualiza `runner_profile.weight_kg`."""
    entry = BodyWeightHistory(
        user_id=user_id,
        weight_kg=weight_kg,
        recorded_at=recorded_at or datetime.now(tz=timezone.utc),
    )
    session.add(entry)
    profile = session.get(RunnerProfile, user_id)
    if profile is not None:
        profile.weight_kg = weight_kg


def get_history(session: Session, user_id: str, limit: int = 30) -> list[BodyWeightHistory]:
    stmt = (
        select(BodyWeightHistory)
        .where(BodyWeightHistory.user_id == user_id)
        .order_by(BodyWeightHistory.recorded_at.desc())
        .limit(limit)
    )
    return list(session.scalars(stmt).all())
