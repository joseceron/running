"""Endpoint /v1/users/me/activities/{id} — lee del cache si existe."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from api.schemas.dashboard import (
    ActivityDetailOut,
    ActivitySample,
    ActivitySplit,
)

router = APIRouter(prefix="/users/me", tags=["activities"])

CACHE_DIR = Path("/tmp/liebre_cache")


def _read_cache(user_id: str) -> ActivityDetailOut | None:
    path = CACHE_DIR / f"activity_{user_id}_latest.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        data["samples"] = [ActivitySample(**s) for s in data.get("samples", [])]
        data["splits"] = [ActivitySplit(**s) for s in data.get("splits", [])]
        return ActivityDetailOut(**data)
    except Exception:
        return None


def _mock_popayan_carrera() -> ActivityDetailOut:
    splits = [
        ActivitySplit(km=1, time_secs=478, pace="7:58", avg_hr=122, max_hr=139, cadence=160, stride_m=0.77, gct_ms=273, elevation_gain_m=4.0),
        ActivitySplit(km=2, time_secs=554, pace="9:14", avg_hr=131, max_hr=145, cadence=158, stride_m=0.68, gct_ms=310, elevation_gain_m=2.0),
        ActivitySplit(km=3, time_secs=656, pace="10:56", avg_hr=133, max_hr=154, cadence=127, stride_m=0.71, gct_ms=299, elevation_gain_m=20.0),
        ActivitySplit(km=4, time_secs=585, pace="9:45", avg_hr=137, max_hr=147, cadence=144, stride_m=0.71, gct_ms=311, elevation_gain_m=22.0),
        ActivitySplit(km=5, time_secs=528, pace="8:48", avg_hr=139, max_hr=149, cadence=152, stride_m=0.73, gct_ms=302, elevation_gain_m=0.0),
        ActivitySplit(km=6, time_secs=128, pace="9:44", avg_hr=133, max_hr=145, cadence=142, stride_m=0.71, gct_ms=347, elevation_gain_m=15.0),
    ]
    samples = []
    t = 0
    distance = 0.0
    while t <= 2930:
        elapsed_min = t / 60
        progress = t / 2930
        hr = 75 + int(elapsed_min * 28) if elapsed_min < 2 else min(154, max(120, int(130 + 8 * (progress - 0.04) + 10 * (0.5 + 0.5 * (((t / 90) % 2) - 1)))))
        if elapsed_min < 8: pace = 480 + int(t / 8) * 2
        elif 9 < elapsed_min < 12: pace = 700
        elif 14 < elapsed_min < 18: pace = 750
        elif 23 < elapsed_min < 26: pace = 720
        else: pace = 520 + int(((t / 60) % 5) * 6)
        cadence = 122 + int((t / 30) % 5) if pace > 650 else 148 + int((t / 25) % 10)
        if pace > 700: cadence = 90
        elevation = int(1740 + 22 * (((t / 600) % 2) - 1))
        d_step = 30.0 / pace
        distance += d_step
        power = int(157 + 50 * (0.5 - abs(0.5 - progress)))
        samples.append(ActivitySample(
            t_secs=t, distance_km=round(distance, 2), pace_secs_per_km=pace,
            hr=hr, cadence=cadence, elevation_m=elevation, power_w=power,
        ))
        t += 30
    return ActivityDetailOut(
        activity_id="22959729618", name="Popayán Carrera",
        started_at="2026-05-21T07:22:00", type="run", distance_km=5.22,
        duration_secs=2930, avg_pace="9:21", avg_hr=133, max_hr=154,
        elevation_gain_m=65, calories=316, avg_cadence=147, avg_stride_m=0.72,
        avg_gct_ms=301, training_effect_aerobic=2.2,
        zone_distribution_pct=[8.0, 70.0, 18.0, 3.4, 0.6],
        samples=samples, splits=splits,
    )


@router.get(
    "/activities/{activity_id}",
    response_model=ActivityDetailOut,
    summary="Detalle de una actividad (cache real si existe, sino mock)",
)
def get_activity(
    activity_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ActivityDetailOut:
    if activity_id == "latest":
        cached = _read_cache(user_id)
        if cached is not None:
            return cached
        return _mock_popayan_carrera()
    if activity_id == "22959729618":
        return _mock_popayan_carrera()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
