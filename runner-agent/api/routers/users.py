"""Endpoints de gestión de usuario y onboarding multi-tenant.

- POST   /v1/users/me/init     — crea/actualiza User + Profile + Garmin creds en una sola request.
- PATCH  /v1/users/me/profile  — actualiza campos parciales del perfil.
- PUT    /v1/users/me/garmin   — actualiza credenciales Garmin (re-valida login).
- DELETE /v1/users/me          — borra cuenta (cascade a todas las tablas).
"""

from __future__ import annotations

import logging
from datetime import date as DateT
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from api.schemas.dashboard import ProfileOut
from data.garmin_client import GarminConnectClient
from memory.repositories import garmin_credentials as creds_repo
from memory.repositories import runner_profile, users

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/me", tags=["users"])


# ─── Schemas ──────────────────────────────────────────────────────────


class InitRequest(BaseModel):
    """Body del POST /init — onboarding inicial del usuario.

    Es idempotente: si el user ya existe, actualiza profile y creds.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    age: int | None = Field(None, ge=10, le=99)
    weight_kg: float | None = Field(None, gt=20, lt=250)
    height_cm: float | None = Field(None, gt=100, lt=230)
    city: str | None = Field(None, max_length=120)
    altitude_msnm: int | None = Field(None, ge=0, le=6000)
    goal_event: Literal["5K", "10K", "21K", "42K", "aprendiendo"] | None = None
    goal_date: DateT | None = None
    goal_time_secs: int | None = Field(None, gt=0)
    injury_history: list[dict] | None = None
    # Credenciales Garmin — opcionales en /init para permitir registro en 2 fases.
    # Si vienen, se cifran y guardan.
    garmin_email: str | None = Field(None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    garmin_password: str | None = Field(None, min_length=1)


class ProfilePatchRequest(BaseModel):
    """Body del PATCH /profile — actualiza solo los campos enviados."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, min_length=1, max_length=120)
    age: int | None = Field(None, ge=10, le=99)
    weight_kg: float | None = Field(None, gt=20, lt=250)
    height_cm: float | None = Field(None, gt=100, lt=230)
    max_hr: int | None = Field(None, ge=100, le=230)
    resting_hr: int | None = Field(None, ge=30, le=100)
    city: str | None = Field(None, max_length=120)
    altitude_msnm: int | None = Field(None, ge=0, le=6000)
    goal_event: Literal["5K", "10K", "21K", "42K", "aprendiendo"] | None = None
    goal_date: DateT | None = None
    goal_time_secs: int | None = Field(None, gt=0)
    injury_history: list[dict] | None = None
    weekly_plan: dict | None = None


class GarminCredsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=1)


class DeleteMeRequest(BaseModel):
    """Confirmación explícita — 'DELETE' literal para evitar borrados accidentales."""
    model_config = ConfigDict(extra="forbid")
    confirm: Literal["DELETE"]


# ─── Helpers ──────────────────────────────────────────────────────────


def _validate_garmin_creds(email: str, password: str) -> None:
    """Hace login real contra Garmin antes de guardar creds.

    Levanta HTTPException 422 si las credenciales no son válidas — así el
    usuario no se queda con creds rotas en BD.
    """
    try:
        GarminConnectClient(email=email, password=password)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Garmin login validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Garmin no aceptó las credenciales: {exc}",
        ) from exc


def _kickoff_initial_sync(user_id: str) -> None:
    """Ejecuta el sync inicial en background tras un onboarding.

    Si falla, registra el error pero no rompe el flujo — el usuario ya tiene
    cuenta y puede reintentar desde el dashboard. Usa una sesión propia
    porque BackgroundTasks corre fuera del scope del request.
    """
    from memory.database import session_scope
    from scripts.sync_garmin_real import (
        _sync_activities_to_db,
        _sync_cronologia,
        _sync_hrv,
    )

    try:
        with session_scope() as db:
            client = GarminConnectClient.for_user(db, user_id)
            _sync_hrv(client, user_id)
            _sync_cronologia(client, user_id)
            _sync_activities_to_db(client, user_id, lookback=50)
        logger.info("Initial sync OK for user_id=%s", user_id)
    except Exception:  # noqa: BLE001
        logger.exception("Initial sync failed for user_id=%s", user_id)


# ─── Endpoints ────────────────────────────────────────────────────────


@router.post(
    "/init",
    response_model=ProfileOut,
    status_code=status.HTTP_200_OK,
    summary="Crea o actualiza User + Profile + credenciales Garmin (onboarding)",
)
def post_init(
    body: InitRequest,
    background: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ProfileOut:
    # 1) Validar creds Garmin ANTES de tocar la BD (si las trae).
    if body.garmin_email and body.garmin_password:
        _validate_garmin_creds(body.garmin_email, body.garmin_password)
    elif bool(body.garmin_email) != bool(body.garmin_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="garmin_email y garmin_password se mandan juntos o no se mandan.",
        )

    # 2) Persistencia transaccional: user + profile + creds. get_db ya commitea
    # al final (o rollback si hubo excepción).
    users.ensure(db, user_id)
    runner_profile.upsert(
        db,
        user_id,
        name=body.name,
        age=body.age,
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        city=body.city,
        altitude_msnm=body.altitude_msnm,
        goal_event=body.goal_event,
        goal_date=body.goal_date,
        goal_time_secs=body.goal_time_secs,
        injury_history=body.injury_history,
    )
    if body.garmin_email and body.garmin_password:
        creds_repo.upsert(
            db,
            user_id,
            email=body.garmin_email,
            password_plain=body.garmin_password,
        )
        users.mark_garmin_connected(db, user_id)
        # Dispara sync inicial DESPUÉS del commit (background, no bloquea response).
        background.add_task(_kickoff_initial_sync, user_id)

    profile = runner_profile.get(db, user_id)
    assert profile is not None
    return ProfileOut.model_validate(profile, from_attributes=True)


@router.patch(
    "/profile",
    response_model=ProfileOut,
    summary="Actualiza campos parciales del perfil",
)
def patch_profile(
    body: ProfilePatchRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ProfileOut:
    existing = runner_profile.get(db, user_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no existe. Llama POST /init primero.",
        )
    # Mantenemos el nombre actual si no llega en el patch
    runner_profile.upsert(
        db,
        user_id,
        name=body.name or existing.name,
        age=body.age,
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        max_hr=body.max_hr,
        resting_hr=body.resting_hr,
        city=body.city,
        altitude_msnm=body.altitude_msnm,
        goal_event=body.goal_event,
        goal_date=body.goal_date,
        goal_time_secs=body.goal_time_secs,
        injury_history=body.injury_history,
        weekly_plan=body.weekly_plan,
    )
    profile = runner_profile.get(db, user_id)
    assert profile is not None
    return ProfileOut.model_validate(profile, from_attributes=True)


@router.put(
    "/garmin",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualiza credenciales Garmin (re-valida login)",
)
def put_garmin(
    body: GarminCredsRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    _validate_garmin_creds(body.email, body.password)
    # users.ensure ANTES del upsert de creds — la FK exige que user exista.
    users.ensure(db, user_id)
    creds_repo.upsert(db, user_id, email=body.email, password_plain=body.password)
    users.mark_garmin_connected(db, user_id)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Borra cuenta completa (cascade a todas las tablas del usuario)",
)
def delete_me(
    body: DeleteMeRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    # body.confirm ya validó que sea "DELETE" via Pydantic Literal
    _ = body
    users.hard_delete(db, user_id)
