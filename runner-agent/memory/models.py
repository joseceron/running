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
    String,
    Text,
    UniqueConstraint,
    func,
)
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
    system_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="profile")


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
