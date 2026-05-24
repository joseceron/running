"""add activities table

Revision ID: 20260524_0001
Revises: 20260521_0001
Create Date: 2026-05-24 13:00:00

Persistencia de actividades sincronizadas desde Garmin. Antes solo cache
efímero en /tmp; ahora histórico real para navegación por fechas.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260524_0001"
down_revision: str | None = "20260521_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("activity_id", sa.String(length=40), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("type_key", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("distance_km", sa.Float, nullable=True),
        sa.Column("duration_secs", sa.Integer, nullable=True),
        sa.Column("avg_hr", sa.Integer, nullable=True),
        sa.Column("max_hr", sa.Integer, nullable=True),
        sa.Column("calories", sa.Integer, nullable=True),
        sa.Column("elevation_gain_m", sa.Float, nullable=True),
        sa.Column("aerobic_te", sa.Float, nullable=True),
        sa.Column("anaerobic_te", sa.Float, nullable=True),
        sa.Column("avg_cadence", sa.Float, nullable=True),
        sa.Column("avg_stride_m", sa.Float, nullable=True),
        sa.Column("avg_gct_ms", sa.Integer, nullable=True),
        sa.Column("vertical_oscillation_cm", sa.Float, nullable=True),
        sa.Column("vertical_ratio_pct", sa.Float, nullable=True),
        sa.Column("zone_distribution_json", sa.Text, nullable=True),
        sa.Column("extended_json", sa.Text, nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "activity_id", name="uq_activity_user_id"),
    )
    op.create_index(
        "ix_activity_user_date", "activities", ["user_id", "date"]
    )


def downgrade() -> None:
    op.drop_index("ix_activity_user_date", table_name="activities")
    op.drop_table("activities")
