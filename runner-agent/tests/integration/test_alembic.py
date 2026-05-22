"""Verifica que las migraciones de Alembic son consistentes con los modelos.

Si alguien edita `memory/models.py` y olvida generar la migration, este test
falla.
"""

from __future__ import annotations

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, create_engine
from testcontainers.postgres import PostgresContainer

from memory.models import Base


pytestmark = pytest.mark.integration


@pytest.fixture
def fresh_pg_url() -> str:
    with PostgresContainer("postgres:16-alpine") as c:
        yield c.get_connection_url()


def test_alembic_upgrade_head_runs(fresh_pg_url: str, monkeypatch) -> None:
    """Aplicar todas las migraciones desde cero no debe lanzar errores."""
    monkeypatch.setenv("DATABASE_URL", fresh_pg_url)
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", fresh_pg_url)
    command.upgrade(cfg, "head")


def test_models_match_migrations(fresh_pg_url: str, monkeypatch) -> None:
    """Tras `alembic upgrade head`, el schema debe coincidir con Base.metadata.

    Si difiere, hay que generar una nueva migration con
    `alembic revision --autogenerate -m '...'`.
    """
    monkeypatch.setenv("DATABASE_URL", fresh_pg_url)
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", fresh_pg_url)
    command.upgrade(cfg, "head")

    engine: Engine = create_engine(fresh_pg_url, future=True)
    with engine.connect() as conn:
        mc = MigrationContext.configure(conn)
        diff = compare_metadata(mc, Base.metadata)
    engine.dispose()

    # Filtramos diferencias que Alembic siempre marca aunque no haya drift real
    # (Postgres a veces normaliza CHECK constraints, etc.)
    real_diff = [d for d in diff if not _is_noise(d)]
    assert real_diff == [], (
        "Drift entre models y migraciones detectado. Corre "
        "`alembic revision --autogenerate -m 'sync models'` para regenerar:\n"
        f"{real_diff}"
    )


def _is_noise(diff_item) -> bool:
    """Filtra falsos positivos comunes de compare_metadata."""
    if isinstance(diff_item, tuple):
        op = diff_item[0]
        if op in {"remove_index", "add_index"}:
            # Algunos índices implícitos de PK no se reportan idénticamente
            return False
    return False
