"""Fixtures compartidas de pytest.

Estrategia:
- `pg_engine` (session scope): levanta un Postgres real en testcontainer y
  aplica todas las migrations de Alembic. Una sola DB por proceso de pytest.
- `db_session` (function scope): abre una transacción savepoint y la revierte
  al terminar el test, dejando la DB limpia para el siguiente.
- `user_a` / `user_b` (function scope): dos user_ids preinsertados para
  validar aislamiento.

Si Docker no está disponible, los tests marcados `integration` se skipean.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from memory.models import Base
from memory.repositories import users


def _docker_available() -> bool:
    return shutil.which("docker") is not None


@pytest.fixture(scope="session")
def pg_engine() -> Iterator[Engine]:
    """Engine contra Postgres real (testcontainer). Skipea si no hay Docker."""
    if not _docker_available():
        pytest.skip("Docker no disponible; saltando tests con Postgres real")

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as container:
        url = container.get_connection_url()  # postgresql+psycopg2://...
        engine = create_engine(url, future=True)
        # Crear todas las tablas via metadata (alternativa: correr Alembic head)
        Base.metadata.create_all(engine)
        yield engine
        engine.dispose()


@pytest.fixture
def db_session(pg_engine: Engine) -> Iterator[Session]:
    """Sesión con savepoint que se rollback al final del test."""
    connection = pg_engine.connect()
    trans = connection.begin()
    SessionLocal = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def user_a(db_session: Session) -> str:
    uid = "user_a_firebase_uid"
    users.ensure(db_session, uid)
    db_session.flush()
    return uid


@pytest.fixture
def user_b(db_session: Session) -> str:
    uid = "user_b_firebase_uid"
    users.ensure(db_session, uid)
    db_session.flush()
    return uid


@pytest.fixture
def alembic_config(tmp_path, pg_engine: Engine):
    """Config de Alembic apuntando al engine de test."""
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "alembic")
    cfg.set_main_option("sqlalchemy.url", str(pg_engine.url))
    return cfg


@pytest.fixture(autouse=True)
def _no_real_secret_manager(monkeypatch):
    """Bloquea acceso accidental a Secret Manager en tests."""
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/nonexistent")
