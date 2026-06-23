"""Repositorio para mediciones de composición corporal."""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from memory.models import BodyComposition


def upsert(
    session: Session,
    user_id: str,
    measured_at: date,
    **fields,
) -> BodyComposition:
    """Inserta o actualiza una medición para la fecha dada."""
    row = (
        session.query(BodyComposition)
        .filter_by(user_id=user_id, measured_at=measured_at)
        .first()
    )
    if row is None:
        row = BodyComposition(user_id=user_id, measured_at=measured_at)
        session.add(row)
    for k, v in fields.items():
        if v is not None:
            setattr(row, k, v)
    session.commit()
    session.refresh(row)
    return row


def get_history(
    session: Session,
    user_id: str,
    limit: int = 52,
) -> list[BodyComposition]:
    """Últimas `limit` mediciones ordenadas por fecha descendente."""
    return (
        session.query(BodyComposition)
        .filter_by(user_id=user_id)
        .order_by(BodyComposition.measured_at.desc())
        .limit(limit)
        .all()
    )


def get_latest(session: Session, user_id: str) -> Optional[BodyComposition]:
    return (
        session.query(BodyComposition)
        .filter_by(user_id=user_id)
        .order_by(BodyComposition.measured_at.desc())
        .first()
    )
