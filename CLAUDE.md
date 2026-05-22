# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Objetivo del proyecto

Agente de IA personalizado para corredores que analiza datos reales de Garmin (biomecánica, HRV, carga) y los combina con literatura científica validada (Scopus + Web of Science) para generar planes de entrenamiento adaptativos semana a semana. El diferenciador es: datos biomecánicos reales + ajuste basado en respuesta individual + respaldo en papers con cita específica.

## Stack tecnológico

- **Lenguaje:** Python 3.11+
- **LLM / Agente:** Claude API (`claude-sonnet-4-6`) via Anthropic Agent SDK
- **Datos Garmin (Fase 1):** `python-garminconnect` (`pip install garminconnect`)
- **Datos Garmin (Fase 2):** Garmin Developer Program (API oficial, push-based)
- **Literatura científica:** `requests` + Scopus API + Web of Science API
- **Persistencia:** SQLite (prototipo) → PostgreSQL (producción)
- **Scheduler:** APScheduler o cron

## Estructura de archivos objetivo

```
runner-agent/
├── .env                        # Credenciales — NO versionar
├── data/
│   ├── garmin_client.py        # Wrapper sobre python-garminconnect
│   ├── scopus_client.py        # Cliente Scopus API
│   └── wos_client.py           # Cliente Web of Science API
├── agents/
│   ├── orchestrator.py         # Agente principal — coordina sub-agentes
│   ├── technique_agent.py      # Análisis técnica de carrera (cadencia, GCT, oscilación)
│   ├── fatigue_agent.py        # HRV, Body Battery, ACWR
│   ├── plan_agent.py           # Generación de plan adaptativo semanal
│   ├── science_agent.py        # Búsqueda y cita de papers
│   └── nutrition_agent.py      # Balance calórico y composición corporal
├── memory/
│   ├── runner_profile.py       # Perfil persistente del corredor
│   └── db.py                   # SQLite schema y operaciones
├── scheduler/
│   └── daily_check.py          # Revisión automática matutina
└── reports/
    └── weekly_report.py        # Generador de reporte semanal
```

## Variables de entorno (.env)

Las credenciales reales están en `/Users/jose.ceron/Documents/emira/.env`. Usar `python-dotenv` para cargarlas. Las variables necesarias son:

```
GARMIN_EMAIL
GARMIN_PASSWORD
SCOPUS_API_KEY        # label: patricia-key
WOS_API_KEY           # plan: Free Institutional Member Plan
ANTHROPIC_API_KEY
DATABASE_URL          # sqlite:///runner_agent.db
```

## APIs externas — detalles clave

### Garmin (`python-garminconnect`)
- Métricas de salud: HRV, Body Battery, FC en reposo, SpO₂, sueño, VO₂Max
- Running Dynamics: cadencia, oscilación vertical, Vertical Ratio, Ground Contact Time (GCT), balance GCT izq/der, longitud de zancada
- No tiene webhooks; hay que hacer polling

### Scopus API
- Base URL: `https://api.elsevier.com` — header `X-ELS-APIKey`
- Rate limit: 1 seg entre búsquedas, 1.2 seg en Abstract Retrieval API
- Queries de ejemplo: `"TITLE-ABS-KEY(running cadence AND injury prevention)"`

### Web of Science API
- Base URL: `https://api.clarivate.com/apis/wos-starter/v1` — header `X-ApiKey`
- Rate limit: ~1 req/seg recomendado
- Queries de ejemplo: `"HRV AND training load AND endurance runners"`

## Arquitectura multi-agente

El orquestador principal (Claude) coordina 5 sub-agentes:

1. **Técnica de Carrera** — detecta degradación de forma durante la actividad; usa cadencia, GCT, balance izq/der
2. **Fatiga y Carga** — calcula ACWR (Acute:Chronic Workload Ratio); alerta si ACWR > 1.5; baseline HRV personal (no poblacional)
3. **Plan Adaptativo** — genera plan semanal ajustado; ritmos basados en zonas reales del corredor ese día
4. **Evidencia Científica** — respalda recomendaciones con papers de Scopus/WoS; distingue RCTs/meta-análisis de estudios observacionales
5. **Nutrición** — cruza gasto calórico (Garmin) con ingesta; detecta déficit calórico crónico y pérdida de masa muscular

### Memoria persistente del corredor
- Perfil: edad, peso, historial de lesiones, metas
- Baseline HRV: se construye en las primeras 2–3 semanas antes de hacer recomendaciones de carga
- Historial de adaptaciones: qué funcionó y qué no para este corredor

## Ciclos de funcionamiento

- **Diario (al despertar):** lee HRV + Body Battery → recomienda tipo de día (carga / recuperación activa / off)
- **Post-entrenamiento:** analiza métricas de sesión vs objetivos, actualiza ACWR
- **Semanal (lunes):** compara plan propuesto vs ejecución real → genera plan ajustado con reporte

## Orden de implementación (Fase 1)

1. `garmin_client.py` — conectar y descargar HRV, Body Battery, última actividad con running dynamics
2. `memory/runner_profile.py` + `db.py` — schema SQLite con perfil, baseline HRV, historial de lesiones
3. `agents/fatigue_agent.py` — análisis HRV vs baseline personal + cálculo ACWR
4. `agents/science_agent.py` — tool de búsqueda Scopus por keyword, retorna abstract + cita formateada
5. `agents/orchestrator.py` — integrar todo en un agente Claude que genere el reporte diario

Validar con datos reales del corredor antes de agregar más sub-agentes.

## Principios de diseño

- **Baseline personal, no poblacional.** El agente construye el baseline de cada corredor en las primeras semanas; no usar valores de literatura como referencia individual.
- **Privacidad de datos.** Las credenciales Garmin dan acceso a datos de salud muy sensibles; nunca al repo, considerar cifrado en BD.
- **El agente detecta y alerta; no reemplaza al médico deportivo** para decisiones clínicas.
