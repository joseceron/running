"""Diagnóstico del día generado por Claude (v2 — multitenant + prompt caching).

Lee los datos del usuario de Postgres, construye un contexto rico, llama a
Claude Sonnet con un system prompt cacheado (>1024 tokens), y devuelve un
JSON estructurado con narrativa causal + acción concreta + cita científica.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import date

from anthropic import Anthropic
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from memory.repositories import hrv as hrv_repo
from memory.repositories import runner_profile, weekly as weekly_repo

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 800

# ─── System prompt grande (cacheable) ──────────────────────────────

SYSTEM_PROMPT = """Eres LIEBRE, el agente personal de entrenamiento de un corredor. Tu misión es \
analizar datos biomecánicos reales de Garmin y respaldar cada recomendación con \
literatura científica validada (Scopus, Web of Science).

PRINCIPIOS NO NEGOCIABLES:
1. BASELINE PERSONAL > rangos poblacionales. Si el corredor tiene <14 noches de HRV \
   registradas, NO emitas recomendaciones de carga basadas en HRV — solo describe \
   estado actual y prioriza completar el baseline.
2. EVIDENCIA CITADA. Cada acción recomendada debe traer un paper que la respalda \
   (autor, año, revista, tipo: RCT/meta-análisis/observacional).
3. INTERPRETACIÓN CAUSAL. NO repitas datos crudos — explica el "por qué" detrás de \
   cada métrica y cómo se relaciona con las otras (HRV ↔ sueño ↔ carga ↔ ACWR).
4. ACCIÓN CONCRETA. La recomendación debe ser específica: tipo de entreno, zona FC, \
   duración, NO genérico ("descansa bien").
5. NO REEMPLAZAS al médico deportivo. Para alertas serias (ACWR > 1.5, HRV deprimido \
   >14 días seguidos), recomienda explícitamente consulta médica.

CONTEXTO PERMANENTE DEL CORREDOR (no varía entre sesiones):
- Entrena a 1,736 msnm (altitud) — esto le da ventaja de adaptación EPO en \
  competencias a menor altitud.
- Historial: desgarro del 49% del sóleo (2024-01-15) — el protocolo de prevención \
  con excéntrico de sóleo NO se debe omitir.
- Meta sub-1:50 en media maratón el 2026-10-01 — requiere VO2max ~52-53; actual ~46.
- Patrón histórico: tiende a entrenar en Z4-Z5 cuando debería estar en Z2 \
  polarizado 80/20 (Seiler 2010).

FORMATO DE RESPUESTA (JSON estricto):
{
  "narrative": "Párrafo de 3-5 oraciones cruzando 2-3 métricas con causalidad. \
  Tono profesional pero accesible. NO uses bullets ni encabezados.",
  "action": "Frase de 1-2 oraciones con la acción específica del día. Verbo en \
  imperativo + zona + duración + por qué.",
  "citation": "Autor (Año) · Revista · Tipo (RCT|Meta|Observacional|Review)",
  "alert_level": "info" | "warn" | "danger"
}

NUNCA agregues texto fuera del JSON. NUNCA inventes papers — usa estos curados:
- Seiler (2010) · Int J Sports Physiol Perform · Review (distribución polarizada 80/20)
- Plews & Buchheit (2017) · J Strength Cond Res · Observacional (HRV monitorización)
- Gabbett (2016) · Br J Sports Med · Review (ACWR y prevención de lesiones)
- Bangsbo et al. (2013) · J Sports Sci · RCT (interval training Z4)
- Kyröläinen et al. (2003) · Int J Sports Med · Observacional (cadencia y economía)
- Bishop & Edge (2006) · Sports Med · Review (repeated sprint ability)
- Buchheit (2014) · Front Physiol · Review (HRV baseline individual)
"""


@dataclass
class DiagnosisResult:
    narrative: str
    action: str
    citation: str
    alert_level: str  # "info" | "warn" | "danger"


def _build_user_message(session: Session, user_id: str) -> str:
    """Construye el contexto dinámico del usuario para el mensaje del turn."""
    profile = runner_profile.get(session, user_id)
    if profile is None:
        raise LookupError(f"Perfil no encontrado para user_id={user_id}")

    baseline = hrv_repo.get_baseline(session, user_id)
    days_recorded, days_required = hrv_repo.get_baseline_progress(session, user_id)
    nights = hrv_repo.get_recent(session, user_id, days=14)
    latest_hrv = nights[0].hrv_rmssd if nights else None
    delta_pct = None
    if latest_hrv is not None and baseline is not None:
        delta_pct = round((latest_hrv - baseline) / baseline * 100, 1)

    weeks = weekly_repo.get_history(session, user_id, n_weeks=3)
    last_week = weeks[0] if weeks else None
    prev_week = weeks[1] if len(weeks) > 1 else None

    days_to_goal = None
    if profile.goal_date:
        days_to_goal = (profile.goal_date - date.today()).days

    payload = {
        "today": date.today().isoformat(),
        "runner": {
            "name": profile.name,
            "age": profile.age,
            "weight_kg": profile.weight_kg,
            "max_hr": profile.max_hr,
            "resting_hr": profile.resting_hr,
            "goal_event": profile.goal_event,
            "goal_date": profile.goal_date.isoformat() if profile.goal_date else None,
            "goal_time_secs": profile.goal_time_secs,
            "days_to_goal": days_to_goal,
        },
        "hrv": {
            "latest_ms": latest_hrv,
            "baseline_ms": baseline,
            "delta_vs_baseline_pct": delta_pct,
            "nights_recorded": days_recorded,
            "nights_required": days_required,
            "baseline_status": (
                "building" if baseline is None
                else "deficit" if (delta_pct is not None and delta_pct < -10)
                else "balanced"
            ),
            "recent_values": [
                {"date": n.date.isoformat(), "ms": n.hrv_rmssd}
                for n in nights[:7]
            ],
        },
        "last_week": (
            {
                "week_start": last_week.week_start.isoformat(),
                "plan_km": last_week.plan_km,
                "executed_km": last_week.executed_km,
                "avg_hrv": last_week.avg_hrv,
                "acwr": last_week.acwr,
                "notes": last_week.agent_notes,
            }
            if last_week else None
        ),
        "prev_week": (
            {
                "executed_km": prev_week.executed_km,
                "acwr": prev_week.acwr,
            }
            if prev_week else None
        ),
    }

    return (
        "Genera el diagnóstico del día para este corredor. Datos actuales:\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nResponde ÚNICAMENTE con el JSON solicitado en tu instrucción de sistema."
    )


def generate_diagnosis(session: Session, user_id: str) -> DiagnosisResult:
    """Llama a Claude con prompt caching y retorna el diagnóstico estructurado."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no definida en el entorno")

    client = Anthropic(api_key=api_key)
    user_message = _build_user_message(session, user_id)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    # Log de uso de cache (telemetría útil)
    usage = response.usage
    logger.info(
        "Diagnosis user=%s tokens in=%s out=%s cache_create=%s cache_read=%s",
        user_id,
        usage.input_tokens,
        usage.output_tokens,
        getattr(usage, "cache_creation_input_tokens", 0),
        getattr(usage, "cache_read_input_tokens", 0),
    )

    raw = response.content[0].text.strip()
    # Limpiar code fences si Claude los puso
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)
    return DiagnosisResult(
        narrative=parsed["narrative"],
        action=parsed["action"],
        citation=parsed["citation"],
        alert_level=parsed.get("alert_level", "info"),
    )
