"""SQLAlchemy engine + sessionmaker para Liebre.

Lee `DATABASE_URL` del entorno. En desarrollo apunta al Postgres del
docker-compose; en producción al Cloud SQL via Auth Proxy / socket Unix.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


def _resolve_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL no está definido. Ejemplos:\n"
            "  dev:   postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre\n"
            "  cloud: postgresql+psycopg2://liebre_app:PASS@/liebre"
            "?host=/cloudsql/liebre-mvp:us-east1:liebre-db"
        )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Engine singleton (lazy)."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            _resolve_database_url(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            future=True,
        )
    return _engine


def get_sessionmaker() -> sessionmaker[Session]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _SessionFactory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager que abre sesión, commitea al final y siempre cierra.

    Uso:
        with session_scope() as session:
            session.add(obj)
    """
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine_for_tests() -> None:
    """Resetea engine y sessionmaker. Útil entre tests que cambian DATABASE_URL."""
    global _engine, _SessionFactory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionFactory = None
