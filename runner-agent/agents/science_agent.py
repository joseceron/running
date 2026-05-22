"""Sub-agente de evidencia científica: Scopus + WoS, clasificación por nivel de evidencia."""
from data import scopus_client, wos_client

EVIDENCE_ORDER = {"strong": 0, "moderate": 1, "weak": 2}

TOPIC_QUERIES = {
    "cadence_injury": (
        "running cadence AND injury prevention",
        "running cadence AND injury prevention",
    ),
    "vertical_oscillation": (
        "vertical oscillation AND running economy",
        "vertical oscillation AND running economy",
    ),
    "hrv_training_load": (
        "HRV AND training load AND endurance runners",
        "HRV AND training load AND endurance runners",
    ),
    "nutrition_running": (
        "nutrition AND running performance AND protein",
        "nutrition AND running performance AND protein",
    ),
    "gct_asymmetry": (
        "ground contact time asymmetry AND running injury",
        "ground contact time asymmetry AND running injury",
    ),
    "acwr_injury": (
        "acute chronic workload ratio AND injury",
        "ACWR AND injury risk AND running",
    ),
}


def find_evidence(topic: str, max_per_source: int = 5) -> list[dict]:
    """
    Busca evidencia científica para un topic.
    topic puede ser una clave de TOPIC_QUERIES o una query libre.
    Retorna papers ordenados por nivel de evidencia (strong primero).
    """
    if topic in TOPIC_QUERIES:
        scopus_q, wos_q = TOPIC_QUERIES[topic]
    else:
        scopus_q = wos_q = topic

    papers = []

    try:
        papers.extend(scopus_client.search(scopus_q, max_results=max_per_source))
    except Exception as e:
        print(f"⚠️  Scopus no disponible: {e}")

    try:
        papers.extend(wos_client.search(wos_q, max_results=max_per_source))
    except Exception as e:
        print(f"⚠️  WoS no disponible: {e}")

    papers.sort(key=lambda p: EVIDENCE_ORDER.get(p.get("evidence_level", "weak"), 2))
    return papers


def format_citation(paper: dict) -> str:
    """Retorna 'Autor (año) Revista — hallazgo clave'."""
    author = paper.get("authors", "Autor desconocido")
    if isinstance(author, list):
        author = author[0] if author else "Autor desconocido"

    year = paper.get("year", "s.f.")
    journal = paper.get("journal", "Revista desconocida")
    title = paper.get("title", "")
    level = paper.get("evidence_level", "weak")
    level_label = {"strong": "★★★", "moderate": "★★☆", "weak": "★☆☆"}.get(level, "")

    abstract = paper.get("abstract", "")
    finding = abstract[:150].rstrip() + "…" if len(abstract) > 150 else abstract

    citation = f"{author} ({year}) {journal} {level_label}"
    if title:
        citation += f"\n  \"{title}\""
    if finding:
        citation += f"\n  {finding}"
    return citation
