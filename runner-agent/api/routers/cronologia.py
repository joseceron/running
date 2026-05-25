"""Endpoint /v1/users/me/cronologia — cronología 24h Body Battery + Stress
+ Sleep + Activity.

Lee del cache `/tmp/liebre_cache/cronologia_{user_id}_{date}.json` si existe
(sync Garmin real). Fallback a datos mock plausibles.
"""

from __future__ import annotations

import json
from datetime import date as DateT
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from api.schemas.dashboard import (
    CronologiaActivity,
    CronologiaOut,
    CronologiaPoint,
)
from api.utils.timezone import local_today

router = APIRouter(prefix="/users/me", tags=["cronologia"])

CACHE_DIR = Path("/tmp/liebre_cache")


def _read_cache(user_id: str, target_date: DateT) -> CronologiaOut | None:
    """Lee el cache de la fecha solicitada si existe."""
    path = CACHE_DIR / f"cronologia_{user_id}_{target_date.isoformat()}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return CronologiaOut(
            points=[CronologiaPoint(**p) for p in data["points"]],
            activities=[CronologiaActivity(**a) for a in data["activities"]],
            summary=data["summary"],
        )
    except Exception:
        return None


def _build_mock_day() -> CronologiaOut:
    """Datos plausibles 24h cuando no hay sync."""
    points: list[CronologiaPoint] = []
    for i in range(97):
        h = i * 0.25
        if h < 6.5:
            bb = int(72 + (h / 6.5) * 23)
            stress = max(5, int(15 - h * 1.5))
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=stress, is_sleeping=True))
        elif h < 7.0:
            bb = 95 - int((h - 6.5) * 10)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=20))
        elif 7.37 <= h <= 8.22:
            progress = (h - 7.37) / 0.85
            bb = int(90 - progress * 10)
            stress = int(40 + progress * 20)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=stress, is_active=True))
        elif h < 12:
            bb = int(80 - (h - 8.22) * 1.2)
            stress = 25 + int((h - 8.22) % 2 * 8)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=stress))
        elif h < 14:
            bb = int(76 - (h - 12) * 2)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=18))
        elif h < 19:
            bb = int(72 - (h - 14) * 2.6)
            cycle = (h - 14) % 1.5
            stress = 35 + int(cycle * 20)
            if h > 17 and h < 17.5:
                stress = 78
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=stress))
        elif h < 22:
            bb = int(59 - (h - 19) * 1.3)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=22))
        else:
            bb = int(55 - (h - 22) * 2.5)
            points.append(CronologiaPoint(hour=h, body_battery=bb, stress=15))

    activities = [CronologiaActivity(hour=7.37, label="Popayán Carrera · 5.22 km", type="run")]
    bb_values = [p.body_battery for p in points if p.body_battery is not None]
    stress_values = [p.stress for p in points if p.stress is not None]
    summary = {
        "body_battery_start": bb_values[0] if bb_values else 0,
        "body_battery_end": bb_values[-1] if bb_values else 0,
        "body_battery_max": max(bb_values) if bb_values else 0,
        "body_battery_min": min(bb_values) if bb_values else 0,
        "stress_avg": int(sum(stress_values) / len(stress_values)) if stress_values else 0,
        "stress_max": max(stress_values) if stress_values else 0,
        "sleep_duration_min": int(6.5 * 60 + 30),
    }
    return CronologiaOut(points=points, activities=activities, summary=summary)


@router.get(
    "/cronologia",
    response_model=CronologiaOut,
    summary="Cronología 24h — datos reales si hay cache, sino mock",
)
def get_cronologia(
    date: DateT | None = Query(default=None, description="YYYY-MM-DD (default: hoy)"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> CronologiaOut:
    target = date or local_today()
    cached = _read_cache(user_id, target)
    if cached is not None:
        return cached
    # Mock solo aplica para el día de hoy; días pasados sin cache devuelven vacío
    if target == local_today():
        return _build_mock_day()
    return CronologiaOut(
        points=[],
        activities=[],
        summary={
            "body_battery_start": 0,
            "body_battery_end": 0,
            "body_battery_max": 0,
            "body_battery_min": 0,
            "stress_avg": 0,
            "stress_max": 0,
            "sleep_duration_min": 0,
        },
    )
