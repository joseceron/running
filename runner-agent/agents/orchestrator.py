"""Orquestador principal: agente Claude que coordina sub-agentes via tool use."""
import json
import os
import sys
from datetime import date, timedelta
from typing import Optional

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

from agents import fatigue_agent, technique_agent, plan_agent, nutrition_agent, science_agent
from data.garmin_client import GarminConnectClient
from memory.runner_profile import (
    get_profile,
    get_hrv_baseline,
    get_weekly_history,
    log_hrv,
    save_weekly_summary,
)

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "get_daily_health",
        "description": "Obtiene métricas de salud de Garmin para una fecha: HRV, Body Battery, FC reposo, sueño.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Fecha ISO (YYYY-MM-DD)"}
            },
            "required": ["date"],
        },
    },
    {
        "name": "get_last_run_dynamics",
        "description": "Obtiene running dynamics de la última actividad de carrera.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "analyze_fatigue",
        "description": "Analiza HRV vs baseline personal, calcula ACWR y genera recomendación del día.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "body_battery": {"type": "number"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "analyze_technique",
        "description": "Analiza técnica de carrera de la última sesión.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "generate_plan",
        "description": "Genera plan semanal adaptativo basado en datos actuales del corredor.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "find_scientific_evidence",
        "description": "Busca evidencia científica en Scopus/WoS para respaldar una recomendación.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Tema de búsqueda o clave: cadence_injury, hrv_training_load, etc.",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_nutrition_status",
        "description": "Revisa alertas de nutrición: déficit calórico crónico y proteína insuficiente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "km_run": {"type": "number"},
            },
            "required": ["date"],
        },
    },
]

_garmin: Optional[GarminConnectClient] = None


def _get_garmin() -> GarminConnectClient:
    global _garmin
    if _garmin is None:
        _garmin = GarminConnectClient()
    return _garmin


def _execute_tool(name: str, inputs: dict) -> str:
    try:
        if name == "get_daily_health":
            g = _get_garmin()
            result = g.get_daily_health(date.fromisoformat(inputs["date"]))
            # Sincronizar HRV al log local
            if result.get("hrv_rmssd"):
                log_hrv(inputs["date"], result["hrv_rmssd"])
            return json.dumps(result)

        elif name == "get_last_run_dynamics":
            g = _get_garmin()
            result = g.get_last_run_dynamics()
            return json.dumps(result)

        elif name == "analyze_fatigue":
            profile = get_profile()
            max_hr = profile.get("max_hr", 190) if profile else 190
            history = get_weekly_history(4)
            recent_acts = [
                {
                    "date": h["week_start"],
                    "distance_m": (h["executed_km"] or 0) * 1000,
                    "avg_hr": 150,
                }
                for h in history
                if h.get("executed_km")
            ]
            result = fatigue_agent.analyze_day(
                date.fromisoformat(inputs["date"]),
                body_battery=inputs.get("body_battery"),
                recent_activities=recent_acts,
                max_hr=max_hr,
            )
            return json.dumps(result)

        elif name == "analyze_technique":
            g = _get_garmin()
            activity = g.get_last_run_dynamics()
            if activity is None:
                return json.dumps({"error": "No se encontró actividad de carrera reciente"})
            result = technique_agent.analyze_session(activity)
            return json.dumps(result)

        elif name == "generate_plan":
            profile = get_profile()
            history = get_weekly_history(4)
            baseline = get_hrv_baseline()
            result = plan_agent.generate_weekly_plan({
                "profile": profile or {},
                "acwr": None,
                "hrv_state": "optimal",
                "weekly_history": history,
            })
            return json.dumps(result)

        elif name == "find_scientific_evidence":
            papers = science_agent.find_evidence(inputs["topic"])
            citations = [science_agent.format_citation(p) for p in papers[:3]]
            return json.dumps({"topic": inputs["topic"], "citations": citations})

        elif name == "get_nutrition_status":
            deficit_alert = nutrition_agent.check_chronic_deficit()
            protein_alert = nutrition_agent.check_protein_alert(
                inputs["date"],
                inputs.get("km_run", 0),
            )
            return json.dumps({
                "chronic_deficit_alert": deficit_alert,
                "protein_alert": protein_alert,
            })

        else:
            return json.dumps({"error": f"Tool desconocido: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})


def _run_agent(system_prompt: str, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Sin respuesta del agente"


SYSTEM_DAILY = """Eres un agente de entrenamiento personalizado para corredores.
Tu rol es analizar los datos de salud matutinos y generar una recomendación clara y motivadora para el día.

Proceso:
1. Obtén métricas de salud de Garmin para hoy
2. Analiza fatiga (HRV vs baseline, ACWR)
3. Ajusta el plan del día según los indicadores
4. Si hay alertas importantes (ACWR > 1.5, HRV suprimido), busca evidencia científica que respalde la recomendación

Formato de respuesta:
- Estado del día (emoji + categoría)
- Métricas clave (HRV, Body Battery, ACWR)
- Recomendación de entrenamiento con ritmos personalizados
- Alertas activas con justificación científica si aplica
- Una frase motivadora final

Idioma: español. Sé directo y práctico. El corredor tiene historial de desgarro de sóleo — prioriza siempre la prevención de lesiones."""


SYSTEM_POST_RUN = """Eres un agente de análisis post-entrenamiento para corredores.
Analiza la última sesión de carrera y genera un resumen técnico y de carga.

Proceso:
1. Obtén running dynamics de la última actividad
2. Analiza técnica: cadencia, GCT, asimetría, degradación de forma
3. Actualiza evaluación de carga
4. Si detectas degradación de forma o asimetría GCT > 52/48, busca evidencia científica

Formato:
- Resumen de sesión (distancia, duración, FC promedio)
- Evaluación técnica por métrica
- Alertas de técnica o lesión
- Evidencia científica si corresponde
- Recomendación para la próxima sesión

Idioma: español."""


SYSTEM_WEEKLY = """Eres un agente de revisión semanal para corredores.
Genera una revisión completa de la semana y el plan de la siguiente.

Proceso:
1. Obtén datos de salud de los últimos 7 días
2. Analiza técnica y tendencias semanales
3. Genera plan adaptativo para la próxima semana
4. Revisa estado nutricional
5. Para cualquier recomendación de cambio de técnica o ajuste de volumen > 20%, busca evidencia científica

Formato:
- Resumen de semana (km, sesiones, tendencias HRV)
- Análisis de técnica
- Plan siguiente semana (7 días con ritmos)
- Estado nutricional
- Evidencia científica para recomendaciones clave
- 1–3 focos prioritarios para la semana

Idioma: español."""


def daily_morning_check() -> str:
    today = date.today().isoformat()
    profile = get_profile()
    if profile is None:
        return "⚠️  Perfil no inicializado. Ejecuta `python init_profile.py` primero."
    return _run_agent(
        SYSTEM_DAILY,
        f"Genera el reporte matutino completo para hoy ({today}). "
        f"Perfil del corredor: {json.dumps(profile)}",
    )


def post_run_analysis() -> str:
    return _run_agent(
        SYSTEM_POST_RUN,
        "Analiza la última sesión de carrera y genera el reporte post-entrenamiento.",
    )


def weekly_review() -> str:
    profile = get_profile()
    history = get_weekly_history(4)
    return _run_agent(
        SYSTEM_WEEKLY,
        f"Genera la revisión semanal completa. "
        f"Perfil: {json.dumps(profile)}. "
        f"Historial de 4 semanas: {json.dumps(history)}",
    )
