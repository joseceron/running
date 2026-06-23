"""SQLAlchemy ORM models — schema multitenant de Liebre.

Cada tabla excepto `science_cache` tiene `user_id` (= Firebase UID) y enforcement
de aislamiento via foreign key + unique constraints compuestas.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


class User(Base):
    """Espejo mínimo de Firebase Auth para FK referencial.

    `user_id` es el UID emitido por Firebase Auth. Se inserta al primer signup
    via `POST /v1/users/me/init` desde el frontend.
    """

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    garmin_connected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    profile: Mapped[Optional["RunnerProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class RunnerProfile(Base):
    """Perfil persistente del corredor — 1:1 con User."""

    __tablename__ = "runner_profile"

    user_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    height_cm: Mapped[Optional[float]] = mapped_column(Float)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    max_hr: Mapped[Optional[int]] = mapped_column(Integer)
    resting_hr: Mapped[Optional[int]] = mapped_column(Integer)
    goal_event: Mapped[Optional[str]] = mapped_column(String(40))
    goal_date: Mapped[Optional[date]] = mapped_column(Date)
    goal_time_secs: Mapped[Optional[int]] = mapped_column(Integer)
    # Multi-tenant: ciudad/altitud por usuario (antes 1736 hardcoded a Popayán)
    city: Mapped[Optional[str]] = mapped_column(String(120))
    altitude_msnm: Mapped[Optional[int]] = mapped_column(Integer)
    # Lista de lesiones históricas: [{name, recovered_at, severity, notes}]
    injury_history: Mapped[Optional[list]] = mapped_column(JSONB)
    # Override del plan semanal default. Formato dict[str, [status, label]] con
    # keys "0".."6" (lun..dom). Si NULL, build_today_action usa DEFAULT_WEEKDAY_PLAN.
    weekly_plan: Mapped[Optional[dict]] = mapped_column(JSONB)
    system_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="profile")


class GarminCredentials(Base):
    """Credenciales Garmin Connect cifradas por usuario.

    Password se cifra con security.crypto.encrypt() antes de persistir. NUNCA
    se loguea ni se devuelve por API. La columna `last_error` guarda el último
    fallo de login (para mostrarle al usuario que debe re-conectar).
    """

    __tablename__ = "garmin_credentials"

    user_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BodyWeightHistory(Base):
    __tablename__ = "body_weight_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_body_weight_user_recorded", "user_id", "recorded_at"),
    )


class HRVLog(Base):
    __tablename__ = "hrv_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hrv_rmssd: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_hrv_user_date"),
        Index("ix_hrv_user_date_desc", "user_id", "date"),
    )


class WeeklyHistory(Base):
    __tablename__ = "weekly_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    plan_km: Mapped[Optional[float]] = mapped_column(Float)
    executed_km: Mapped[Optional[float]] = mapped_column(Float)
    avg_hrv: Mapped[Optional[float]] = mapped_column(Float)
    avg_body_battery: Mapped[Optional[float]] = mapped_column(Float)
    acwr: Mapped[Optional[float]] = mapped_column(Float)
    agent_notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("user_id", "week_start", name="uq_weekly_user_week"),
    )


class NutritionLog(Base):
    __tablename__ = "nutrition_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    kcal: Mapped[Optional[float]] = mapped_column(Float)
    protein_g: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="logged", nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_nutrition_user_date"),
    )


class Activity(Base):
    """Actividades sincronizadas desde Garmin — persistencia para histórico.

    Antes solo había cache efímero en /tmp; sin esta tabla, navegar a fechas
    pasadas mostraba "sesión no realizada" aunque sí hubiera entrenado, porque
    el cache del día anterior se sobrescribía con cada sync.
    """

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    activity_id: Mapped[str] = mapped_column(String(40), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    type_key: Mapped[str] = mapped_column(String(40), nullable=False)  # running, walking, strength_training, etc
    name: Mapped[Optional[str]] = mapped_column(String(255))
    distance_km: Mapped[Optional[float]] = mapped_column(Float)
    duration_secs: Mapped[Optional[int]] = mapped_column(Integer)
    avg_hr: Mapped[Optional[int]] = mapped_column(Integer)
    max_hr: Mapped[Optional[int]] = mapped_column(Integer)
    calories: Mapped[Optional[int]] = mapped_column(Integer)
    elevation_gain_m: Mapped[Optional[float]] = mapped_column(Float)
    aerobic_te: Mapped[Optional[float]] = mapped_column(Float)
    anaerobic_te: Mapped[Optional[float]] = mapped_column(Float)
    avg_cadence: Mapped[Optional[float]] = mapped_column(Float)
    avg_stride_m: Mapped[Optional[float]] = mapped_column(Float)
    avg_gct_ms: Mapped[Optional[int]] = mapped_column(Integer)
    vertical_oscillation_cm: Mapped[Optional[float]] = mapped_column(Float)
    vertical_ratio_pct: Mapped[Optional[float]] = mapped_column(Float)
    # Distribución por zonas (Z1..Z5) como JSON serializado en texto
    zone_distribution_json: Mapped[Optional[str]] = mapped_column(Text)
    # Payload extendido (samples + splits) opcional, también JSON
    extended_json: Mapped[Optional[str]] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "activity_id", name="uq_activity_user_id"),
        Index("ix_activity_user_date", "user_id", "date"),
    )


class BodyComposition(Base):
    """Mediciones de composición corporal desde báscula inteligente.

    Se registra ~1 vez/semana (lunes mañana, en ayunas).
    Permite ver la curva de adaptación: grasa ↓, masa muscular ↑.
    """

    __tablename__ = "body_composition"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    measured_at: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    bmi: Mapped[Optional[float]] = mapped_column(Float)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Float)
    subcutaneous_fat_pct: Mapped[Optional[float]] = mapped_column(Float)
    visceral_fat: Mapped[Optional[float]] = mapped_column(Float)
    fat_free_weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    skeletal_muscle_pct: Mapped[Optional[float]] = mapped_column(Float)
    muscle_mass_kg: Mapped[Optional[float]] = mapped_column(Float)
    bone_mass_kg: Mapped[Optional[float]] = mapped_column(Float)
    body_water_pct: Mapped[Optional[float]] = mapped_column(Float)
    bmr_kcal: Mapped[Optional[int]] = mapped_column(Integer)
    metabolic_age: Mapped[Optional[int]] = mapped_column(Integer)
    protein_pct: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "measured_at", name="uq_body_comp_user_date"),
        Index("ix_body_comp_user_date", "user_id", "measured_at"),
    )


class ScienceCache(Base):
    """Caché compartido de papers de Scopus/WoS — NO contiene user_id."""

    __tablename__ = "science_cache"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    results_json: Mapped[str] = mapped_column(Text, nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("query", "source", name="uq_science_query_source"),
    )
