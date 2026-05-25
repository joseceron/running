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
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agents.today_action_builder import build_today_action
from api.utils.timezone import local_today
from memory.repositories import hrv as hrv_repo
from memory.repositories import runner_profile, weekly as weekly_repo

CACHE_DIR = Path("/tmp/liebre_cache")


def _load_today_activities(user_id: str, today: date) -> list[dict]:
    """Lee el cache de cronología de hoy y extrae las actividades ejecutadas.

    Las actividades vienen del sync (sync_garmin_real._sync_cronologia) ya
    formateadas en `{"hour": ..., "label": "...", "type": "..."}`.
    Si no hay cache fresco, retorna lista vacía.
    """
    path = CACHE_DIR / f"cronologia_{user_id}_{today.isoformat()}.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data.get("activities") or []
    except Exception:
        return []

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

CONTEXTO DINÁMICO DEL CORREDOR: El campo `runner` del payload trae los datos \
permanentes de ESTE usuario (nombre, edad, peso, altitud de entrenamiento, lesiones \
históricas, meta y fecha). USA ESOS valores — NUNCA asumas datos de otro corredor \
(altitudes específicas, lesiones específicas, metas específicas). Si el payload \
no incluye un dato, no lo inventes — di "no tengo registrado X".

IMPORTANTE: revisa siempre el campo `activities_today` del payload antes de \
recomendar un entreno. Si ya ejecutó sesiones hoy, la "acción recomendada" debe \
enfocarse en recuperación, complemento o sesión de mañana — NO mandes a entrenar \
algo que ya hizo.

6. CONSISTENCIA CON EL PLAN (NO NEGOCIABLE). El payload trae `today_action` con \
   la decisión inequívoca para hoy, calculada por el motor de plan + carga + HRV. \
   Tu campo `action` DEBE ser estrictamente coherente con `today_action.status`:
   - `today_action.status == "rest"`: tu `action` describe recuperación (sueño, \
     hidratación, movilidad, foam roller, caminata conversacional). PROHIBIDO \
     mandar a correr, rodar, Z2 ni nada que sume carga aeróbica.
   - `today_action.status == "active_recovery"`: tu `action` describe movilidad o \
     caminata muy ligera Z1 ≤30 min. PROHIBIDO sesión de calidad o volumen alto.
   - `today_action.status == "trained_already"`: tu `action` describe post-recovery \
     (estiramientos, nutrición post, sueño temprano). PROHIBIDO sumar otra sesión.
   - `today_action.status == "train"`: tu `action` debe coincidir con el verbo y \
     la zona de `today_action.headline` (no inventes una sesión diferente).
   Si la narrativa fisiológica te invita a contradecir, prevalece `today_action`. \
   La narrativa puede explicar el porqué, pero la acción se subordina al plan.

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
- Achten & Jeukendrup (2004) · Int J Sports Med · Review (FatMax zona aeróbica)
- Lamberts et al. (2009) · Br J Sports Med · Observacional (cardiac drift como índice de carga)
- Stöggl & Sperlich (2014) · Front Physiol · Review (polarizado vs umbral en endurance)
- Mujika & Padilla (2003) · Med Sci Sports Exerc · Review (tapering pre-competencia)
- Bompa & Buzzichelli (2018) · libro · texto referente (periodización)

GLOSARIO TÉCNICO (úsalo con precisión, no inventes equivalencias):
- ACWR (Acute:Chronic Workload Ratio): cociente carga aguda (7 días) / crónica (28 días). \
  Zona segura 0.8–1.3, riesgo elevado >1.5 (Gabbett 2016).
- HRV (heart rate variability, RMSSD): mide modulación parasimpática. Caída >1 SD del \
  baseline personal sugiere estrés autonómico — no entrenar carga ese día.
- Z2 (zona 2 aeróbica): ~60-70% FCmax. Zona donde se construye base mitocondrial sin \
  acumular fatiga del SNC.
- Z4 (zona umbral/VO2): ~80-90% FCmax. Sesiones cortas, alta calidad, requieren \
  recuperación posterior.
- Cardiac drift: aumento de FC manteniendo pace constante. <5% en 60 min = eficiencia \
  cardiovascular alta; >8% = deshidratación, fatiga o calor.
- Cadencia: pasos por minuto. ≥170 spm asociado a menor impacto y mejor economía \
  (Kyröläinen 2003).

REGLAS DE ESCRITURA:
- Usa el nombre del corredor cuando lo tengas (`runner.name`), no "el corredor".
- Si el campo `runner.altitude_msnm` está presente y >1500, menciona el efecto \
  EPO/adaptación a la altura. Si <500 o ausente, no lo menciones.
- Si `runner.injury_history` trae lesiones recuperadas hace >2 años, NO frenes \
  progresión por ellas — pero menciona ejercicios preventivos relevantes.
- Si `runner.injury_history` trae lesiones recientes (<1 año), pasa el tono a \
  conservador y recomienda evaluación profesional ante cualquier dolor.
- Si `runner.days_to_goal` < 14 días y la meta es una carrera, prioriza tapering, \
  no sumes volumen nuevo.
"""


@dataclass
class DiagnosisResult:
    narrative: str
    action: str
    citation: str
    alert_level: str  # "info" | "warn" | "danger"


def _build_user_message(
    session: Session, user_id: str, target_date: date | None = None
) -> str:
    """Construye el contexto dinámico del usuario para el mensaje del turn."""
    profile = runner_profile.get(session, user_id)
    if profile is None:
        raise LookupError(f"Perfil no encontrado para user_id={user_id}")

    target = target_date or local_today()

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
        days_to_goal = (profile.goal_date - target).days

    activities_today = _load_today_activities(user_id, target)

    # Decisión inequívoca de "qué hacer hoy" — misma lógica que consume
    # /report. La inyectamos para que el LLM no contradiga al plan (issue
    # observada 2026-05-24: "DESCANSA HOY" + LLM diciendo "ejecuta 45 min").
    activity_labels = [
        a.get("label", "")
        for a in activities_today
        if isinstance(a, dict) and a.get("label")
    ]
    today_action = build_today_action(
        target=target,
        activity_labels=activity_labels,
        acwr=last_week.acwr if last_week else None,
        hrv_today=latest_hrv,
        hrv_baseline=baseline,
        weekday_plan=profile.weekly_plan,
    )

    payload = {
        "today": target.isoformat(),
        "activities_today": activities_today,
        "training_status_today": (
            "trained" if activities_today else "no_session_yet"
        ),
        "today_action": {
            "status": today_action["status"],
            "temporal": today_action["temporal"],
            "headline": today_action["headline"],
            "short_reason": today_action["short_reason"],
            "reasons": today_action["reasons"],
        },
        "runner": {
            "name": profile.name,
            "age": profile.age,
            "weight_kg": profile.weight_kg,
            "height_cm": profile.height_cm,
            "max_hr": profile.max_hr,
            "resting_hr": profile.resting_hr,
            "city": profile.city,
            "altitude_msnm": profile.altitude_msnm,
            "injury_history": profile.injury_history or [],
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


def generate_diagnosis(
    session: Session, user_id: str, target_date: date | None = None
) -> DiagnosisResult:
    """Llama a Claude con prompt caching y retorna el diagnóstico estructurado."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no definida en el entorno")

    client = Anthropic(api_key=api_key)
    user_message = _build_user_message(session, user_id, target_date)

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
