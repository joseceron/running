"""Operaciones sobre `runner_profile` (perfil 1:1 con User)."""

from __future__ import annotations

from datetime import date as DateT
from typing import Any

from sqlalchemy.orm import Session

from memory.models import RunnerProfile


def upsert(
    session: Session,
    user_id: str,
    *,
    name: str,
    age: int | None = None,
    height_cm: float | None = None,
    weight_kg: float | None = None,
    max_hr: int | None = None,
    resting_hr: int | None = None,
    goal_event: str | None = None,
    goal_date: DateT | None = None,
    goal_time_secs: int | None = None,
    city: str | None = None,
    altitude_msnm: int | None = None,
    injury_history: list[dict] | None = None,
    weekly_plan: dict | None = None,
) -> RunnerProfile:
    """Crea o actualiza el perfil del usuario.

    Nunca borra registros de otros usuarios — el `user_id` está hardcoded
    por la clave primaria. Solo actualiza los campos cuyo valor no es None,
    es decir: PATCH-like (los kwargs ausentes preservan el valor previo).
    """
    profile = session.get(RunnerProfile, user_id)
    if profile is None:
        profile = RunnerProfile(user_id=user_id, name=name)
        session.add(profile)
    profile.name = name
    if age is not None:
        profile.age = age
    if height_cm is not None:
        profile.height_cm = height_cm
    if weight_kg is not None:
        profile.weight_kg = weight_kg
    if max_hr is not None:
        profile.max_hr = max_hr
    if resting_hr is not None:
        profile.resting_hr = resting_hr
    if goal_event is not None:
        profile.goal_event = goal_event
    if goal_date is not None:
        profile.goal_date = goal_date
    if goal_time_secs is not None:
        profile.goal_time_secs = goal_time_secs
    if city is not None:
        profile.city = city
    if altitude_msnm is not None:
        profile.altitude_msnm = altitude_msnm
    if injury_history is not None:
        profile.injury_history = injury_history
    if weekly_plan is not None:
        profile.weekly_plan = weekly_plan
    session.flush()
    return profile


def get(session: Session, user_id: str) -> RunnerProfile | None:
    return session.get(RunnerProfile, user_id)


def get_as_dict(session: Session, user_id: str) -> dict[str, Any] | None:
    p = get(session, user_id)
    if p is None:
        return None
    return {
        "user_id": p.user_id,
        "name": p.name,
        "age": p.age,
        "height_cm": p.height_cm,
        "weight_kg": p.weight_kg,
        "max_hr": p.max_hr,
        "resting_hr": p.resting_hr,
        "goal_event": p.goal_event,
        "goal_date": p.goal_date.isoformat() if p.goal_date else None,
        "goal_time_secs": p.goal_time_secs,
        "city": p.city,
        "altitude_msnm": p.altitude_msnm,
        "injury_history": p.injury_history,
        "weekly_plan": p.weekly_plan,
        "system_start": p.system_start.isoformat(),
    }


def set_goal(
    session: Session,
    user_id: str,
    *,
    event: str,
    goal_date: DateT,
    goal_time_secs: int | None = None,
) -> None:
    profile = session.get(RunnerProfile, user_id)
    if profile is None:
        raise LookupError(f"runner_profile no existe para user_id={user_id!r}")
    profile.goal_event = event
    profile.goal_date = goal_date
    profile.goal_time_secs = goal_time_secs
