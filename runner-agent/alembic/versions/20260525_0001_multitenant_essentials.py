"""multi-tenant essentials: garmin_credentials + runner_profile extensions

Revision ID: 20260525_0001
Revises: 20260524_0001
Create Date: 2026-05-25 09:00:00

Fase 1 del plan multi-tenant. Una migration combinada porque ambos cambios son
prerequisito del onboarding wizard y deben aplicarse atómicamente:

1. Tabla `garmin_credentials` — password cifrado con Fernet por usuario.
   Reemplaza la única cuenta del .env por una credencial por user_id.
2. Extiende `runner_profile` con `city`, `altitude_msnm`, `injury_history` (JSONB)
   y `weekly_plan` (JSONB override del DEFAULT_WEEKDAY_PLAN). Antes `altitude_msnm`
   estaba hardcodeado a 1736 (Popayán) en runner-agent/api/routers/report.py.
3. Backfill del user dev `jose_dev_uid` con sus valores reales para no romper
   el dashboard local mientras se completa el flujo.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260525_0001"
down_revision: str | None = "20260524_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) Nueva tabla garmin_credentials
    op.create_table(
        "garmin_credentials",
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 2) Extensiones a runner_profile
    op.add_column(
        "runner_profile",
        sa.Column("city", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "runner_profile",
        sa.Column("altitude_msnm", sa.Integer, nullable=True),
    )
    op.add_column(
        "runner_profile",
        sa.Column("injury_history", JSONB, nullable=True),
    )
    op.add_column(
        "runner_profile",
        sa.Column("weekly_plan", JSONB, nullable=True),
    )

    # 3) Backfill del user dev — los valores que estaban hardcoded en el código
    op.execute(
        """
        UPDATE runner_profile
        SET city = 'Popayán',
            altitude_msnm = 1736,
            injury_history = CAST('[{"name": "Desgarro del 49% del sóleo", "recovered_at": "2021-01-01", "severity": "moderate", "notes": "5 años sin dolor ni recaídas; no es restricción activa"}]' AS JSONB)
        WHERE user_id = 'jose_dev_uid'
          AND altitude_msnm IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("runner_profile", "weekly_plan")
    op.drop_column("runner_profile", "injury_history")
    op.drop_column("runner_profile", "altitude_msnm")
    op.drop_column("runner_profile", "city")
    op.drop_table("garmin_credentials")
