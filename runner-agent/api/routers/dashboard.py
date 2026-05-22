"""Endpoints del dashboard — sirven datos al frontend Next.js."""

from __future__ import annotations

from datetime import date as DateT

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from api.schemas.dashboard import (
    DashboardOut,
    HRVNight,
    HRVOut,
    ProfileOut,
    WeeklyEntry,
    WeeklyOut,
)
from memory.repositories import hrv, runner_profile, weekly

router = APIRouter(prefix="/users/me", tags=["dashboard"])


def _classify_hrv(latest: float, baseline: float | None) -> str:
    if baseline is None:
        return "building_baseline"
    delta_pct = (latest - baseline) / baseline * 100
    if delta_pct >= -3:
        return "optimal"
    if delta_pct >= -10:
        return "reduced"
    return "suppressed"


def _build_hrv(session: Session, user_id: str) -> HRVOut:
    nights = hrv.get_recent(session, user_id, days=14)
    days_recorded, days_required = hrv.get_baseline_progress(session, user_id)
    baseline = hrv.get_baseline(session, user_id)
    latest_value = nights[0].hrv_rmssd if nights else None
    latest_delta_pct = None
    if latest_value is not None and baseline is not None:
        latest_delta_pct = round((latest_value - baseline) / baseline * 100, 2)
    return HRVOut(
        nights=[HRVNight(date=n.date, hrv_rmssd=n.hrv_rmssd) for n in nights],
        baseline_ms=round(baseline, 2) if baseline else None,
        days_recorded=days_recorded,
        days_required=days_required,
        latest_value=latest_value,
        latest_delta_pct=latest_delta_pct,
        status=_classify_hrv(latest_value, baseline) if latest_value else "building_baseline",
    )


def _build_weekly(session: Session, user_id: str) -> WeeklyOut:
    rows = weekly.get_history(session, user_id, n_weeks=6)
    return WeeklyOut(
        weeks=[
            WeeklyEntry(
                week_start=w.week_start,
                plan_km=w.plan_km,
                executed_km=w.executed_km,
                avg_hrv=w.avg_hrv,
                avg_body_battery=w.avg_body_battery,
                acwr=w.acwr,
                agent_notes=w.agent_notes,
            )
            for w in rows
        ]
    )


@router.get(
    "/profile",
    response_model=ProfileOut,
    summary="Perfil del corredor",
)
def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ProfileOut:
    profile = runner_profile.get(db, user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no creado. Completa el onboarding primero.",
        )
    return ProfileOut.model_validate(profile, from_attributes=True)


@router.get(
    "/hrv",
    response_model=HRVOut,
    summary="HRV reciente + baseline personal",
)
def get_hrv(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> HRVOut:
    return _build_hrv(db, user_id)


@router.get(
    "/weekly",
    response_model=WeeklyOut,
    summary="Historial semanal (últimas 6 semanas)",
)
def get_weekly(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> WeeklyOut:
    return _build_weekly(db, user_id)


@router.get(
    "/dashboard",
    response_model=DashboardOut,
    summary="Payload agregado del dashboard (1 sola request)",
)
def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> DashboardOut:
    profile = runner_profile.get(db, user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no creado.",
        )
    days_to_goal = None
    if profile.goal_date:
        days_to_goal = (profile.goal_date - DateT.today()).days
    return DashboardOut(
        profile=ProfileOut.model_validate(profile, from_attributes=True),
        hrv=_build_hrv(db, user_id),
        weekly=_build_weekly(db, user_id),
        days_to_goal=days_to_goal,
    )
