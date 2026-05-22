"""Operaciones sobre la tabla `users` (espejo de Firebase Auth)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from memory.models import User


def ensure(session: Session, user_id: str) -> User:
    """Idempotente: crea el user si no existe; en cualquier caso lo retorna."""
    user = session.get(User, user_id)
    if user is None:
        user = User(user_id=user_id)
        session.add(user)
        session.flush()
    return user


def get(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)


def mark_garmin_connected(session: Session, user_id: str) -> None:
    user = session.get(User, user_id)
    if user is None:
        raise LookupError(f"user_id {user_id!r} no existe")
    user.garmin_connected_at = datetime.now(tz=timezone.utc)


def soft_delete(session: Session, user_id: str) -> None:
    """Marca el user como borrado. El purge físico (cascade) lo hace
    `hard_delete` solo desde el endpoint DELETE explícito."""
    user = session.get(User, user_id)
    if user is None:
        return
    user.deleted_at = datetime.now(tz=timezone.utc)


def hard_delete(session: Session, user_id: str) -> None:
    """Borrado físico — cascadea a profile, hrv_log, weekly_history,
    nutrition_log, body_weight_history."""
    user = session.get(User, user_id)
    if user is not None:
        session.delete(user)


def list_active_user_ids(session: Session) -> list[str]:
    """Para el fanout diario — usuarios no borrados con Garmin conectado."""
    stmt = (
        select(User.user_id)
        .where(User.deleted_at.is_(None))
        .where(User.garmin_connected_at.is_not(None))
    )
    return list(session.scalars(stmt).all())
