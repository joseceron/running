"""Endpoints del dashboard — sirven datos al frontend Next.js."""

from __future__ import annotations

from datetime import date as DateT, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user_id, get_db
from api.utils.timezone import local_today
from api.schemas.dashboard import (
    DashboardOut,
    HRVNight,
    HRVOut,
    ProfileOut,
    SleepOut,
    UpcomingTraining,
    UpcomingTrainingsOut,
    WeeklyEntry,
    WeeklyOut,
)
import logging
from memory.repositories import hrv, runner_profile, weekly
from data.garmin_client import GarminConnectClient

logger = logging.getLogger(__name__)

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


def _build_upcoming(session: Session, user_id: str) -> UpcomingTrainingsOut:
    """Genera plan placeholder de próximos 5 entrenos.

    Hasta que conectemos plan_agent multi-tenant, retorna una semana modelo
    polarizada 80/20 ajustada al estado HRV actual.
    """
    today = local_today()
    baseline_ms = hrv.get_baseline(session, user_id)
    days_recorded = len(hrv.get_recent(session, user_id, days=14))
    building = baseline_ms is None

    # Plan modelo: si HRV building → todo Z2; si balanced → introduce Z3/Z4
    template = (
        [
            ("Rodaje Z2", 40, "Z2", 6.0,
             "HRV construyendo baseline — Z2 favorece adaptación aeróbica sin estrés autónomo."),
            ("Fuerza", 45, "—", None,
             "Núcleo + sóleo excéntrico. Crítico tras tu lesión 2024-01-15."),
            ("Rodaje Z2", 35, "Z2", 5.2,
             "Mantén intensidad baja. Cadencia objetivo 170 spm con drills en lugar."),
            ("Movilidad", 30, "Z1", None,
             "Recuperación activa. Calistenia + foam roller."),
            ("Rodaje largo Z2", 60, "Z2", 9.0,
             "Sesión clave de la semana. Aumenta volumen aeróbico hacia tu meta 21K."),
        ]
        if building
        else [
            ("Tempo Z3", 35, "Z3", 6.0,
             "Tu baseline HRV está estable — toca primera sesión de calidad de la semana."),
            ("Fuerza", 45, "—", None,
             "Núcleo + sóleo excéntrico. Protocolo de prevención post-lesión."),
            ("Rodaje Z2", 50, "Z2", 7.5,
             "Reconstrucción aeróbica entre sesiones intensas."),
            ("Series Z4", 40, "Z4", 6.0,
             "8x400 en Z4 con recuperación Z1. Activa VO2max para acercarte a sub-1:50."),
            ("Rodaje largo Z2", 80, "Z2", 12.0,
             "Long run de fin de semana. Base aeróbica para la maratón media."),
        ]
    )

    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    sessions: list[UpcomingTraining] = []
    for i, (typ, dur, zone, dist, why) in enumerate(template):
        d = today + timedelta(days=i + 1)
        label = (
            "Mañana" if i == 0
            else "Pasado mañana" if i == 1
            else day_names[d.weekday()]
        )
        sessions.append(
            UpcomingTraining(
                day_label=f"{label} · {d.strftime('%d %b').lower()}",
                relative_days=i + 1,
                type=typ,
                duration_min=dur,
                zone_target=zone,
                distance_km=dist,
                rationale=why,
            )
        )
    return UpcomingTrainingsOut(sessions=sessions)


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
    "/upcoming-trainings",
    response_model=UpcomingTrainingsOut,
    summary="Próximos 5 entrenamientos planificados",
)
def get_upcoming(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UpcomingTrainingsOut:
    return _build_upcoming(db, user_id)


def _build_sleep(session: Session, user_id: str) -> SleepOut | None:
    """Obtiene sueño de hoy desde Garmin. Falla silencioso — no rompe el dashboard."""
    try:
        client = GarminConnectClient.for_user(session, user_id)
        today = local_today()
        health = client.get_daily_health(today)
        deep_s = health.get("sleep_deep_seconds") or 0
        rem_s  = health.get("sleep_rem_seconds")  or 0
        light_s = health.get("sleep_light_seconds") or 0
        total_s = deep_s + rem_s + light_s
        if total_s == 0:
            return None
        return SleepOut(
            date=today,
            total_min=round(total_s / 60),
            deep_min=round(deep_s / 60),
            rem_min=round(rem_s / 60),
            light_min=round(light_s / 60),
            awake_min=None,
            sleep_score=health.get("sleep_score"),
        )
    except Exception:
        logger.warning("Sleep fetch failed — skipping", exc_info=False)
        return None


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
        days_to_goal = (profile.goal_date - local_today()).days
    return DashboardOut(
        profile=ProfileOut.model_validate(profile, from_attributes=True),
        hrv=_build_hrv(db, user_id),
        weekly=_build_weekly(db, user_id),
        upcoming=_build_upcoming(db, user_id),
        days_to_goal=days_to_goal,
        sleep=_build_sleep(db, user_id),
    )
