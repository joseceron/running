"""Pydantic schemas de respuesta — generan automáticamente la doc Swagger."""

from __future__ import annotations

from datetime import date as DateT, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    """Perfil del corredor."""

    user_id: str
    name: str
    age: int | None = Field(None, example=36)
    height_cm: float | None = Field(None, example=170.0)
    weight_kg: float | None = Field(None, example=68.0)
    max_hr: int | None = Field(None, example=190)
    resting_hr: int | None = Field(None, example=51)
    goal_event: Literal["5K", "10K", "21K", "42K", "aprendiendo"] | None = Field(
        None, example="21K"
    )
    goal_date: DateT | None = Field(None, example="2026-10-01")
    goal_time_secs: int | None = Field(None, example=6600)
    system_start: datetime


class HRVNight(BaseModel):
    """Una noche de HRV."""

    date: DateT
    hrv_rmssd: float = Field(..., example=55.0)


class HRVOut(BaseModel):
    """Estado HRV: noches recientes + baseline personal + estado de progreso."""

    nights: list[HRVNight]
    baseline_ms: float | None = Field(
        None, description="Media móvil de últimos 7 días sobre 14 registros; null si <14"
    )
    days_recorded: int = Field(..., example=8)
    days_required: int = Field(..., example=14)
    latest_value: float | None = Field(None, example=52.0)
    latest_delta_pct: float | None = Field(
        None,
        description="Delta % del último valor vs baseline (negativo = bajo baseline)",
    )
    status: Literal["optimal", "reduced", "suppressed", "building_baseline"] = Field(
        ..., example="building_baseline"
    )


class WeeklyEntry(BaseModel):
    week_start: DateT
    plan_km: float | None = None
    executed_km: float | None = None
    avg_hrv: float | None = None
    avg_body_battery: float | None = None
    acwr: float | None = None
    agent_notes: str | None = None


class WeeklyOut(BaseModel):
    weeks: list[WeeklyEntry]


class DashboardOut(BaseModel):
    """Payload agregado consumido por la home del dashboard."""

    profile: ProfileOut
    hrv: HRVOut
    weekly: WeeklyOut
    days_to_goal: int | None = Field(
        None, description="Días desde hoy hasta la fecha de la meta"
    )
