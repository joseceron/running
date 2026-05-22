"""initial multitenant schema

Revision ID: 20260521_0001
Revises:
Create Date: 2026-05-21 23:15:00

Schema inicial de Liebre — todas las tablas con `user_id` excepto `science_cache`
que es caché global compartido.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260521_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("garmin_connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "runner_profile",
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("max_hr", sa.Integer(), nullable=True),
        sa.Column("resting_hr", sa.Integer(), nullable=True),
        sa.Column("goal_event", sa.String(length=40), nullable=True),
        sa.Column("goal_date", sa.Date(), nullable=True),
        sa.Column("goal_time_secs", sa.Integer(), nullable=True),
        sa.Column(
            "system_start",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "body_weight_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_body_weight_user_recorded",
        "body_weight_history",
        ["user_id", "recorded_at"],
    )

    op.create_table(
        "hrv_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("hrv_rmssd", sa.Float(), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_hrv_user_date"),
    )
    op.create_index("ix_hrv_user_date_desc", "hrv_log", ["user_id", "date"])

    op.create_table(
        "weekly_history",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("plan_km", sa.Float(), nullable=True),
        sa.Column("executed_km", sa.Float(), nullable=True),
        sa.Column("avg_hrv", sa.Float(), nullable=True),
        sa.Column("avg_body_battery", sa.Float(), nullable=True),
        sa.Column("acwr", sa.Float(), nullable=True),
        sa.Column("agent_notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("user_id", "week_start", name="uq_weekly_user_week"),
    )

    op.create_table(
        "nutrition_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("kcal", sa.Float(), nullable=True),
        sa.Column("protein_g", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="logged",
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "date", name="uq_nutrition_user_date"),
    )

    op.create_table(
        "science_cache",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("results_json", sa.Text(), nullable=False),
        sa.Column(
            "cached_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("query", "source", name="uq_science_query_source"),
    )


def downgrade() -> None:
    op.drop_table("science_cache")
    op.drop_table("nutrition_log")
    op.drop_table("weekly_history")
    op.drop_index("ix_hrv_user_date_desc", table_name="hrv_log")
    op.drop_table("hrv_log")
    op.drop_index("ix_body_weight_user_recorded", table_name="body_weight_history")
    op.drop_table("body_weight_history")
    op.drop_table("runner_profile")
    op.drop_table("users")
