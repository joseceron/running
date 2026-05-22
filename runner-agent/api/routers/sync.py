"""Endpoint POST /v1/users/me/sync — dispara sync Garmin → Postgres + cache.

Importa las funciones del script directamente (no spawn proceso) para
mejor manejo de errores y telemetría.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from data.garmin_client import GarminConnectClient
from scripts.sync_garmin_real import (
    _sync_cronologia,
    _sync_hrv,
    _sync_last_activity,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/me", tags=["sync"])


class SyncResult(BaseModel):
    started_at: str
    finished_at: str
    duration_secs: float
    hrv_nights: int
    cronologia_ok: bool
    activity_ok: bool
    error: str | None = None


@router.post(
    "/sync",
    response_model=SyncResult,
    summary="Sincroniza datos reales de Garmin (HRV + Body Battery + última actividad)",
)
def post_sync(
    user_id: str = Depends(get_current_user_id),
    _db: Session = Depends(get_db),
) -> SyncResult:
    started = datetime.now(tz=timezone.utc)
    try:
        client = GarminConnectClient()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Garmin login falló")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No pude conectar con Garmin: {exc}",
        ) from exc

    hrv_nights = 0
    cronologia_ok = False
    activity_ok = False
    error_msg: str | None = None

    try:
        hrv_nights = _sync_hrv(client, user_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Sync HRV falló")
        error_msg = f"HRV: {exc}"

    try:
        cronologia_ok = _sync_cronologia(client, user_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Sync cronología falló")
        error_msg = (error_msg or "") + f" | Cronología: {exc}"

    try:
        activity_ok = _sync_last_activity(client, user_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Sync actividad falló")
        error_msg = (error_msg or "") + f" | Actividad: {exc}"

    finished = datetime.now(tz=timezone.utc)
    return SyncResult(
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        duration_secs=round((finished - started).total_seconds(), 2),
        hrv_nights=hrv_nights,
        cronologia_ok=cronologia_ok,
        activity_ok=activity_ok,
        error=error_msg,
    )
