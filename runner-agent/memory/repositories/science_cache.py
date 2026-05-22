"""Caché compartido de Scopus/WoS (sin user_id — global)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from memory.models import ScienceCache

DEFAULT_TTL_DAYS = 7


def get(
    session: Session,
    query: str,
    source: str,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> list[dict[str, Any]] | None:
    """Retorna el resultado cacheado si existe y no está vencido."""
    stmt = (
        select(ScienceCache)
        .where(ScienceCache.query == query)
        .where(ScienceCache.source == source)
    )
    row = session.scalar(stmt)
    if row is None:
        return None
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=ttl_days)
    if row.cached_at < cutoff:
        return None
    return json.loads(row.results_json)


def put(
    session: Session,
    query: str,
    source: str,
    results: list[dict[str, Any]],
) -> None:
    """Upsert con marca de tiempo actualizada."""
    payload = json.dumps(results)
    now = datetime.now(tz=timezone.utc)
    stmt = (
        pg_insert(ScienceCache)
        .values(query=query, source=source, results_json=payload, cached_at=now)
        .on_conflict_do_update(
            constraint="uq_science_query_source",
            set_={"results_json": payload, "cached_at": now},
        )
    )
    session.execute(stmt)
