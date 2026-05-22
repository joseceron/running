"""Cliente Web of Science Starter API con rate limiting y caché SQLite."""
import json
import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from memory.db import get_connection, init_db

load_dotenv()

BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1"
CACHE_TTL_DAYS = 7


def _get_cached(query: str) -> list[dict] | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT results_json, cached_at FROM science_cache WHERE query=? AND source='wos'",
        (query,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    cached_at = datetime.fromisoformat(row["cached_at"])
    if datetime.utcnow() - cached_at > timedelta(days=CACHE_TTL_DAYS):
        return None
    return json.loads(row["results_json"])


def _save_cache(query: str, results: list[dict]):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO science_cache (query, source, results_json, cached_at)
        VALUES (?, 'wos', ?, ?)
        """,
        (query, json.dumps(results), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def _classify_evidence(abstract: str) -> str:
    text = abstract.lower()
    if any(k in text for k in ["meta-analysis", "meta analysis", "systematic review"]):
        return "strong"
    if any(k in text for k in ["randomized", "randomised", "rct", "controlled trial"]):
        return "strong"
    if any(k in text for k in ["cohort", "case-control", "prospective"]):
        return "moderate"
    return "weak"


def search(query: str, max_results: int = 5) -> list[dict]:
    """Busca papers en WoS Starter API. Retorna lista con metadatos + nivel de evidencia."""
    init_db()
    cached = _get_cached(query)
    if cached is not None:
        return cached

    api_key = os.environ.get("WOS_API_KEY", "")
    headers = {"X-ApiKey": api_key, "Accept": "application/json"}
    params = {
        "q": query,
        "limit": max_results,
        "page": 1,
        "db": "WOS",
    }

    time.sleep(1)
    response = requests.get(
        f"{BASE_URL}/documents",
        headers=headers,
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    hits = response.json().get("hits", [])
    results = []
    for h in hits:
        title = (h.get("title") or {}).get("value", "")
        names = h.get("names", {}).get("authors", [])
        first_author = names[0].get("displayName", "") if names else ""
        source_info = h.get("source", {})
        journal = source_info.get("sourceTitle", "")
        year = str(source_info.get("publishYear", ""))
        identifiers = h.get("identifiers", {})
        doi = next(
            (i.get("value") for i in identifiers.get("doi", []) if i.get("value")),
            "",
        )
        abstract = (h.get("abstract") or {}).get("value", "") or ""
        results.append({
            "title": title,
            "authors": first_author,
            "journal": journal,
            "year": year,
            "doi": doi,
            "abstract": abstract,
            "source": "wos",
            "evidence_level": _classify_evidence(abstract),
        })

    _save_cache(query, results)
    return results
