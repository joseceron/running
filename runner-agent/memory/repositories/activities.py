"""Operaciones sobre la tabla `activities` — persistencia de sesiones Garmin."""

from __future__ import annotations

import json
from datetime import date as DateT
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from memory.models import Activity


def upsert(session: Session, user_id: str, payload: dict[str, Any]) -> None:
    """UPSERT idempotente de una actividad por (user_id, activity_id).

    payload espera estructura "Garmin-shaped" (output de get_activities):
    `activityId`, `activityType.typeKey`, `startTimeLocal`, `distance`, `duration`,
    `averageHR`, `maxHR`, `calories`, `elevationGain`, `aerobicTrainingEffect`,
    `anaerobicTrainingEffect`, `averageRunningCadenceInStepsPerMinute`, `strideLength`,
    `groundContactTime`, `verticalOscillation`, `verticalRatio`, plus opcionalmente
    `zone_distribution_pct: list[float]` y `extended: dict` ya parseados.
    """
    activity_id = str(payload["activityId"])
    started_local = (payload.get("startTimeLocal") or "")[:19]
    started_at = None
    activity_date = None
    if started_local:
        from datetime import datetime
        try:
            started_at = datetime.fromisoformat(started_local)
            activity_date = started_at.date()
        except ValueError:
            pass
    if activity_date is None:
        activity_date = DateT.today()

    type_key = (payload.get("activityType") or {}).get("typeKey", "unknown")
    name = payload.get("activityName") or None
    distance_km = round((payload.get("distance") or 0) / 1000, 3) if payload.get("distance") else None
    duration_secs = int(payload.get("duration") or 0) or None
    avg_hr = int(payload["averageHR"]) if payload.get("averageHR") else None
    max_hr = int(payload["maxHR"]) if payload.get("maxHR") else None
    calories = int(payload["calories"]) if payload.get("calories") else None
    elevation = float(payload["elevationGain"]) if payload.get("elevationGain") else None
    aerobic_te = float(payload["aerobicTrainingEffect"]) if payload.get("aerobicTrainingEffect") else None
    anaerobic_te = float(payload["anaerobicTrainingEffect"]) if payload.get("anaerobicTrainingEffect") else None
    avg_cadence = float(payload["averageRunningCadenceInStepsPerMinute"]) if payload.get("averageRunningCadenceInStepsPerMinute") else None
    avg_stride = round(float(payload["strideLength"]) / 100, 2) if payload.get("strideLength") else None
    avg_gct = int(payload["groundContactTime"]) if payload.get("groundContactTime") else None
    vert_osc = float(payload["verticalOscillation"]) if payload.get("verticalOscillation") else None
    vert_ratio = float(payload["verticalRatio"]) if payload.get("verticalRatio") else None

    zone_pct = payload.get("zone_distribution_pct")
    zone_json = json.dumps(zone_pct) if zone_pct else None
    extended_json = json.dumps(payload["extended"]) if payload.get("extended") else None

    set_values = {
        "date": activity_date,
        "started_at": started_at,
        "type_key": type_key,
        "name": name,
        "distance_km": distance_km,
        "duration_secs": duration_secs,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "calories": calories,
        "elevation_gain_m": elevation,
        "aerobic_te": aerobic_te,
        "anaerobic_te": anaerobic_te,
        "avg_cadence": avg_cadence,
        "avg_stride_m": avg_stride,
        "avg_gct_ms": avg_gct,
        "vertical_oscillation_cm": vert_osc,
        "vertical_ratio_pct": vert_ratio,
        "zone_distribution_json": zone_json,
        "extended_json": extended_json,
    }
    insert_values = {**set_values, "user_id": user_id, "activity_id": activity_id}

    stmt = (
        pg_insert(Activity)
        .values(**insert_values)
        .on_conflict_do_update(constraint="uq_activity_user_id", set_=set_values)
    )
    session.execute(stmt)


def get_by_date(session: Session, user_id: str, target_date: DateT) -> list[Activity]:
    """Todas las actividades de un usuario en una fecha específica."""
    stmt = (
        select(Activity)
        .where(Activity.user_id == user_id, Activity.date == target_date)
        .order_by(Activity.started_at.asc())
    )
    return list(session.execute(stmt).scalars().all())


def get_by_id(session: Session, user_id: str, activity_id: str) -> Activity | None:
    stmt = select(Activity).where(
        Activity.user_id == user_id, Activity.activity_id == activity_id
    )
    return session.execute(stmt).scalar_one_or_none()


def get_latest(
    session: Session, user_id: str, type_key: str | None = None, limit: int = 1
) -> list[Activity]:
    """Últimas N actividades del usuario, opcionalmente filtradas por tipo."""
    stmt = select(Activity).where(Activity.user_id == user_id)
    if type_key:
        stmt = stmt.where(Activity.type_key == type_key)
    stmt = stmt.order_by(Activity.started_at.desc()).limit(limit)
    return list(session.execute(stmt).scalars().all())


def get_recent(session: Session, user_id: str, days: int = 7) -> list[Activity]:
    """Últimos N días — todas las actividades del rango."""
    from datetime import timedelta

    cutoff = DateT.today() - timedelta(days=days)
    stmt = (
        select(Activity)
        .where(Activity.user_id == user_id, Activity.date >= cutoff)
        .order_by(Activity.started_at.desc())
    )
    return list(session.execute(stmt).scalars().all())
