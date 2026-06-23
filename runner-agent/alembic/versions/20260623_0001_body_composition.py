"""body_composition table — mediciones de báscula inteligente

Revision ID: 20260623_0001
Revises: 20260525_0001
Create Date: 2026-06-23

Persiste mediciones semanales de composición corporal para visualizar
la curva de adaptación: grasa ↓, masa muscular ↑ a lo largo del tiempo.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260623_0001"
down_revision = "20260525_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "body_composition",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(128), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("measured_at", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Float()),
        sa.Column("bmi", sa.Float()),
        sa.Column("body_fat_pct", sa.Float()),
        sa.Column("subcutaneous_fat_pct", sa.Float()),
        sa.Column("visceral_fat", sa.Float()),
        sa.Column("fat_free_weight_kg", sa.Float()),
        sa.Column("skeletal_muscle_pct", sa.Float()),
        sa.Column("muscle_mass_kg", sa.Float()),
        sa.Column("bone_mass_kg", sa.Float()),
        sa.Column("body_water_pct", sa.Float()),
        sa.Column("bmr_kcal", sa.Integer()),
        sa.Column("metabolic_age", sa.Integer()),
        sa.Column("protein_pct", sa.Float()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "measured_at", name="uq_body_comp_user_date"),
    )
    op.create_index("ix_body_comp_user_date", "body_composition", ["user_id", "measured_at"])


def downgrade() -> None:
    op.drop_index("ix_body_comp_user_date", "body_composition")
    op.drop_table("body_composition")
