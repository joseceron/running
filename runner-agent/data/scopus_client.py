"""Cliente Scopus API con rate limiting y caché SQLite."""
import json
import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from memory.db import get_connection, init_db

load_dotenv()

BASE_URL = "https://api.elsevier.com/content"
CACHE_TTL_DAYS = 7


def _get_cached(query: str) -> list[dict] | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT results_json, cached_at FROM science_cache WHERE query=? AND source='scopus'",
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
        VALUES (?, 'scopus', ?, ?)
        """,
        (query, json.dumps(results), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def _classify_evidence(abstract: str, pub_type: str = "") -> str:
    text = (abstract + " " + pub_type).lower()
    if any(k in text for k in ["meta-analysis", "meta analysis", "systematic review"]):
        return "strong"
    if any(k in text for k in ["randomized", "randomised", "rct", "controlled trial"]):
        return "strong"
    if any(k in text for k in ["cohort", "case-control", "prospective"]):
        return "moderate"
    return "weak"


def search(query: str, max_results: int = 5) -> list[dict]:
    """Busca papers en Scopus. Retorna lista de dicts con metadatos + nivel de evidencia."""
    init_db()
    cached = _get_cached(query)
    if cached is not None:
        return cached

    api_key = os.environ.get("SCOPUS_API_KEY", "")
    headers = {"X-ELS-APIKey": api_key, "Accept": "application/json"}
    params = {
        "query": f"TITLE-ABS-KEY({query})",
        "count": max_results,
        "field": "dc:title,dc:creator,prism:publicationName,prism:coverDate,prism:doi,dc:description,subtypeDescription",
    }

    time.sleep(1)
    response = requests.get(
        f"{BASE_URL}/search/scopus",
        headers=headers,
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    entries = response.json().get("search-results", {}).get("entry", [])
    results = []
    for e in entries:
        abstract = e.get("dc:description", "") or ""
        pub_type = e.get("subtypeDescription", "") or ""
        results.append({
            "title": e.get("dc:title", ""),
            "authors": e.get("dc:creator", ""),
            "journal": e.get("prism:publicationName", ""),
            "year": (e.get("prism:coverDate", "") or "")[:4],
            "doi": e.get("prism:doi", ""),
            "abstract": abstract,
            "source": "scopus",
            "evidence_level": _classify_evidence(abstract, pub_type),
        })
        time.sleep(1.2)  # Abstract Retrieval API rate limit

    _save_cache(query, results)
    return results
