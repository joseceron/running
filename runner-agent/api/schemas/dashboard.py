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
    # Multi-tenant: datos per-user que antes eran hardcoded
    city: str | None = Field(None, example="Popayán")
    altitude_msnm: int | None = Field(None, example=1736)
    injury_history: list[dict] | None = Field(
        None,
        description="Lista de {name, recovered_at, severity, notes}",
        example=[{"name": "Desgarro sóleo", "recovered_at": "2021-01-01", "severity": "moderate"}],
    )
    weekly_plan: dict | None = Field(
        None,
        description="Override del plan semanal. dict[str, [status, label]] con keys '0'..'6' (lun..dom)",
    )
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


class ActivitySplit(BaseModel):
    km: int
    time_secs: int = Field(..., example=478)  # 7:58
    pace: str = Field(..., example="7:58")
    avg_hr: int
    max_hr: int
    cadence: int
    stride_m: float
    gct_ms: int
    elevation_gain_m: float


class ActivitySample(BaseModel):
    """Punto de la serie temporal dentro de la actividad."""

    t_secs: int  # tiempo desde inicio
    distance_km: float
    pace_secs_per_km: int | None = None
    hr: int | None = None
    cadence: int | None = None
    elevation_m: int | None = None
    power_w: int | None = None


class ActivityDetailOut(BaseModel):
    activity_id: str
    name: str
    started_at: str = Field(..., example="2026-05-21T07:22:00")
    type: Literal["run", "walk", "bike", "swim"] = "run"
    distance_km: float
    duration_secs: int
    avg_pace: str = Field(..., example="9:21")
    avg_hr: int
    max_hr: int
    elevation_gain_m: int
    calories: int
    avg_cadence: int
    avg_stride_m: float
    avg_gct_ms: int
    training_effect_aerobic: float
    zone_distribution_pct: list[float] = Field(..., example=[10, 70, 18, 2, 0])
    samples: list[ActivitySample]
    splits: list[ActivitySplit]


class CronologiaPoint(BaseModel):
    """Un punto en la cronología 24h (hora decimal + valores)."""

    hour: float = Field(..., example=14.5, description="Hora decimal 0-24")
    body_battery: int | None = Field(None, example=68)
    stress: int | None = Field(None, example=45, description="0-100")
    is_sleeping: bool = False
    is_active: bool = False


class CronologiaActivity(BaseModel):
    hour: float
    label: str = Field(..., example="Popayán Carrera")
    type: str = Field(..., example="run")


class CronologiaOut(BaseModel):
    points: list[CronologiaPoint]
    activities: list[CronologiaActivity]
    summary: dict = Field(
        ...,
        example={
            "body_battery_start": 100,
            "body_battery_end": 52,
            "body_battery_max": 100,
            "body_battery_min": 48,
            "stress_avg": 22,
            "stress_max": 78,
            "sleep_duration_min": 392,
        },
    )


class DiagnosisOut(BaseModel):
    """Diagnóstico del día generado por Claude (orchestrator v2)."""

    narrative: str = Field(..., example="Tu HRV de 52 ms está dentro del rango funcional...")
    action: str = Field(..., example="Hoy: rodaje Z2 de 35-40 min con drills de cadencia.")
    citation: str = Field(..., example="Seiler (2010) · Int J Sports Physiol Perform · Review")
    alert_level: Literal["info", "warn", "danger"] = Field(..., example="info")
    generated_at: str = Field(..., example="2026-05-21T22:30:00Z")


class UpcomingTraining(BaseModel):
    """Una sesión de entrenamiento planificada."""

    day_label: str = Field(..., example="Mañana · Vie 22 may")
    relative_days: int = Field(..., example=1, description="Días desde hoy (0=hoy)")
    type: Literal[
        "Rodaje Z2",
        "Series Z4",
        "Tempo Z3",
        "Rodaje largo Z2",
        "Fuerza",
        "Movilidad",
        "Descanso",
    ]
    duration_min: int = Field(..., example=40)
    zone_target: Literal["Z1", "Z2", "Z3", "Z4", "Z5", "—"] = Field(..., example="Z2")
    distance_km: float | None = Field(None, example=6.5)
    rationale: str = Field(
        ..., example="Tu HRV está construyendo baseline — Z2 favorece la adaptación aeróbica sin estrés autónomo."
    )


class UpcomingTrainingsOut(BaseModel):
    sessions: list[UpcomingTraining]


class DashboardOut(BaseModel):
    """Payload agregado consumido por la home del dashboard."""

    profile: ProfileOut
    hrv: HRVOut
    weekly: WeeklyOut
    upcoming: UpcomingTrainingsOut
    days_to_goal: int | None = Field(
        None, description="Días desde hoy hasta la fecha de la meta"
    )
