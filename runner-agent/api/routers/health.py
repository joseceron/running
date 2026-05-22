"""Health checks para Cloud Run."""

from __future__ import annotations

from fastapi import APIRouter

from api.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
