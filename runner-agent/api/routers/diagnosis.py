"""Endpoint POST /v1/users/me/diagnosis — invoca a Claude para generar el
diagnóstico del día. Cache simple en memoria por (user_id, fecha) para no
quemar tokens en cada refresh del dashboard.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from agents.diagnostic_v2 import generate_diagnosis
from api.deps import get_current_user_id, get_db
from api.schemas.dashboard import DiagnosisOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/me", tags=["diagnosis"])

# Cache en memoria: {(user_id, fecha_iso): DiagnosisOut}
_cache: dict[tuple[str, str], DiagnosisOut] = {}


@router.get(
    "/diagnosis",
    response_model=DiagnosisOut,
    summary="Diagnóstico del día generado por Claude (cacheado por día)",
)
def get_diagnosis(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> DiagnosisOut:
    today_iso = date.today().isoformat()
    cache_key = (user_id, today_iso)

    if cache_key in _cache:
        return _cache[cache_key]

    try:
        result = generate_diagnosis(db, user_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_diagnosis falló para user=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No pude generar el diagnóstico: {exc}",
        ) from exc

    out = DiagnosisOut(
        narrative=result.narrative,
        action=result.action,
        citation=result.citation,
        alert_level=result.alert_level,
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
    )
    _cache[cache_key] = out
    return out


@router.post(
    "/diagnosis/refresh",
    response_model=DiagnosisOut,
    summary="Fuerza regeneración del diagnóstico (invalida cache)",
)
def refresh_diagnosis(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> DiagnosisOut:
    today_iso = date.today().isoformat()
    _cache.pop((user_id, today_iso), None)
    return get_diagnosis(user_id=user_id, db=db)
