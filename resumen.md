# App Agéntica para Corredores — Resumen de Arquitectura y Decisiones

> Documento generado para continuar implementación en Claude Code.  
> Fecha: 2026-05-10

---

## 1. Objetivo del proyecto

Construir un agente de IA altamente personalizado para corredores que:

- Analice los datos reales del corredor (no promedios genéricos) para ajustar planes de entrenamiento semana a semana.
- Evalúe **técnica de carrera** usando métricas de biomecánica disponibles en Garmin.
- Controle **nutrición y composición corporal** para evitar pérdida de masa muscular durante alto volumen.
- Detecte **riesgo de lesión** antes de que ocurra, basándose en tendencias de HRV, fatiga y carga acumulada.
- Respalde cada recomendación con **literatura científica validada** (Scopus + Web of Science), no con datos no verificados.

Caso de referencia que inspira el estándar de excelencia: una corredora en Washington DC que, con guía profesional individualizada, completó el Maratón de Boston en 1 año de entrenamiento — un logro que muchos corredores no alcanzan en 8 años con planes genéricos.

---

## 2. Decisión de conexión a Garmin

### Opción A — `python-garminconnect` (GitHub, no oficial)
- **Repositorio:** https://github.com/cyberjunky/python-garminconnect
- **Instalación:** `pip install garminconnect`
- **Pros:** Disponible hoy sin aprobación, cubre todos los datos necesarios, fácil de usar en Python.
- **Contras:** No oficial, puede romperse si Garmin cambia su backend. No tiene webhooks/push.
- **Uso recomendado:** Prototipo y desarrollo inicial (Fase 1).

### Opción B — Garmin Connect Developer Program (API oficial)
- **Portal:** https://developerportal.garmin.com/developer-programs/connect-developer-api
- **Docs:** https://developer.garmin.com/gc-developer-program/
- **Pros:** Oficial y estable. Push-based (datos llegan en segundos tras sincronización del reloj). Soporta múltiples usuarios. Tiene Health API, Activity API y Training API.
- **Contras:** Requiere proceso de aprobación (semanas). Diseñado para integración B2B.
- **Uso recomendado:** Producción y escala (Fase 2).

### Decisión adoptada
**Fase 1 (inmediato):** Usar `python-garminconnect` para construir y validar el agente.  
**Fase 2 (en paralelo):** Aplicar al Developer Program oficial. Cuando se apruebe, migrar solo la capa de ingesta de datos sin tocar la lógica del agente.

> **Nota importante:** El archivo `connection-to-apps.md` (metodología de bridge Java/RMI para interceptar apps sin API pública) **NO aplica** a Garmin porque Garmin sí tiene API pública. Ese enfoque es útil para otras integraciones futuras con software propietario (como ERPs tipo Celeste).

---

## 3. Métricas disponibles en Garmin

### Salud y recuperación
| Métrica | Descripción |
|---|---|
| HRV (Heart Rate Variability) | Mejor proxy de recuperación del sistema nervioso autónomo |
| Body Battery | Indicador Garmin 0–100 de energía disponible (combina HRV, estrés y sueño) |
| Frecuencia cardíaca en reposo | Tendencia de base aeróbica y fatiga acumulada |
| SpO₂ | Saturación de oxígeno nocturna |
| Sueño (staging + score) | Fases REM, profundo, ligero — calidad real del descanso |
| Nivel de estrés diario | Medido por variabilidad HRV durante el día |
| VO₂Max estimado | Capacidad aeróbica máxima (running y ciclismo) |

### Técnica de carrera (Running Dynamics)
| Métrica | Descripción | Por qué importa |
|---|---|---|
| Cadencia (pasos/min) | Frecuencia de zancada | Cadencias 170–180 reducen impacto articular |
| Oscilación vertical (cm) | Altura del "bote" en cada zancada | Menor = más eficiente |
| Vertical Ratio (%) | Oscilación / longitud de zancada | Indicador global de economía de carrera |
| Ground Contact Time (ms) | Tiempo de contacto con el suelo | Menor = mayor potencia de propulsión |
| Balance GCT izq/der (%) | Simetría entre piernas | Asimetrías > 52/48 indican compensaciones o lesión latente |
| Longitud de zancada (m) | Distancia por paso | Combinada con cadencia define el ritmo |

### Actividad y composición
- Pasos, pisos, calorías activas y BMR
- Composición corporal (con báscula Garmin Index): peso, % grasa, masa muscular, masa ósea, agua corporal
- GPS y splits por kilómetro
- Tiempo en zonas de frecuencia cardíaca (Z1–Z5)
- Historial de más de 100 tipos de actividad

---

## 4. Fuentes de literatura científica

### Scopus (Elsevier)
```
Base URL:  https://api.elsevier.com
Header:    X-ELS-APIKey: <API_KEY>
Label:     patricia-key
```
- Rate limit: 1 seg entre búsquedas, 1.2 seg en Abstract Retrieval API.
- Útil para: buscar papers por keyword, obtener abstracts, filtrar por año y revista.

### Web of Science (Clarivate)
```
Base URL:  https://api.clarivate.com/apis/wos-starter/v1
Header:    X-ApiKey: <API_KEY>
Plan:      Free Institutional Member Plan
```
- Rate limit: ~1 req/seg recomendado.
- Útil para: búsquedas por tema, autores, citaciones.

> Las credenciales reales están en `/Users/jose.ceron/Documents/emira/.env`. No incluirlas en el código fuente; leerlas con `python-dotenv`.

### Queries de ejemplo para el dominio
```python
# Scopus — buscar papers sobre cadencia y lesiones
query = "TITLE-ABS-KEY(running cadence AND injury prevention)"

# Scopus — economía de carrera y oscilación vertical
query = "TITLE-ABS-KEY(vertical oscillation AND running economy)"

# WoS — HRV y carga de entrenamiento
query = "HRV AND training load AND endurance runners"

# Scopus — nutrición en corredores de fondo
query = "TITLE-ABS-KEY(energy availability AND distance running AND body composition)"
```

---

## 5. Arquitectura del agente

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENTE ORQUESTADOR                       │
│                     (Claude como motor LLM)                     │
└──────────┬──────────────┬──────────────┬──────────────┬─────────┘
           │              │              │              │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌───▼───────┐ ┌───▼──────────┐
    │  Sub-agente │ │ Sub-agente │ │ Sub-agente│ │  Sub-agente  │
    │  Técnica    │ │  Fatiga &  │ │  Plan     │ │  Evidencia   │
    │  de Carrera │ │  Carga     │ │ Adaptativo│ │  Científica  │
    └──────┬──────┘ └─────┬──────┘ └───┬───────┘ └───┬──────────┘
           │              │            │              │
    ┌──────▼──────────────▼────────────▼──────────────▼──────────┐
    │              CAPA DE DATOS                                  │
    │   Garmin API (python-garminconnect → oficial)               │
    │   Scopus API  |  Web of Science API  |  Nutrición (input)   │
    └─────────────────────────────────────────────────────────────┘
```

### Sub-agentes y responsabilidades

**1. Sub-agente Técnica de Carrera**
- Analiza cadencia, oscilación vertical, GCT y balance izq/der.
- Detecta degradación de forma durante la carrera (ej. cadencia cae 8% en km 15 → fatiga de forma).
- Busca en Scopus el rango óptimo de cada métrica para el perfil del corredor.

**2. Sub-agente Fatiga y Carga**
- Monitorea HRV vs baseline personal (no vs promedios poblacionales).
- Evalúa Body Battery al despertar → recomienda si es día de carga o recuperación.
- Calcula Acute:Chronic Workload Ratio (ACWR) para detectar sobreentrenamiento.
- Alerta si el corredor entra en zona de riesgo de lesión (ACWR > 1.5).

**3. Sub-agente Plan Adaptativo**
- Genera plan semanal ajustado a los datos reales de la semana anterior.
- Personaliza ritmos (no "corre a 5:30/km" sino "corre a tu ritmo Z2 real, que hoy es 5:48/km dado tu HRV").
- Ajusta volumen y distribución de intensidad (80/20, polarizado, etc.) según respuesta individual.

**4. Sub-agente Evidencia Científica**
- Para cada recomendación importante, busca el respaldo en Scopus o WoS.
- Cita el paper específico: autor, revista, año, hallazgo clave.
- Diferencia entre evidencia fuerte (RCTs, meta-análisis) y débil (estudios observacionales).

**5. Sub-agente Nutrición**
- Cruza gasto calórico (Garmin) con ingesta reportada por el corredor.
- Detecta déficit calórico crónico que compromete composición corporal.
- Caso específico a prevenir: pérdida de masa muscular por alto volumen sin suficiente ingesta proteica.
- Integración posible: Cronometer API para ingesta automática.

**6. Memoria del Corredor (persistente)**
- Perfil: edad, peso, historial de lesiones, metas (ej. clasificar Boston, bajar de 4h en maratón).
- Baseline HRV personal (se construye en las primeras 2–3 semanas).
- Historial de adaptaciones: qué funcionó y qué no para este corredor específico.
- Alertas previas y su resolución.

---

## 6. Ciclo de funcionamiento (semanal)

```
Lunes (revisión semanal)
  1. Agente descarga datos de la semana anterior desde Garmin
  2. Compara: plan propuesto vs ejecución real
  3. Analiza tendencias: HRV, Body Battery, métricas de técnica
  4. Consulta Scopus/WoS si detecta patrones que requieren respaldo científico
  5. Genera plan ajustado para la semana siguiente
  6. Entrega reporte al corredor con insights y justificación

Diario (al despertar)
  1. Lee HRV nocturno y Body Battery del día
  2. Recomienda: día de carga / día de recuperación activa / día off
  3. Ajusta el entrenamiento del día si los indicadores lo justifican
  4. Alerta si detecta riesgo de sobreentrenamiento o asimetría de técnica

Post-entrenamiento
  1. Analiza métricas de la sesión vs objetivos
  2. Detecta degradación de forma durante la actividad
  3. Actualiza modelo de carga acumulada (ACWR)
```

---

## 7. Stack tecnológico recomendado

| Componente | Tecnología | Razón |
|---|---|---|
| Lenguaje principal | Python 3.11+ | Ecosistema de data science, `garminconnect`, `requests` |
| LLM / Agente | Claude API (claude-sonnet-4-6) | Razonamiento, síntesis de papers, personalización |
| SDK agente | Anthropic Agent SDK | Orquestación de sub-agentes, tool use |
| Datos Garmin (Fase 1) | `python-garminconnect` | Inmediato, sin aprobación |
| Datos Garmin (Fase 2) | Garmin Developer Program | Push-based, producción |
| Literatura científica | `requests` + Scopus API + WoS API | Credenciales ya disponibles |
| Persistencia | SQLite (prototipo) → PostgreSQL (prod) | Memoria del corredor, historial |
| Scheduler | APScheduler o cron | Revisión diaria automática |
| Nutrición (opcional) | Cronometer API o input manual | Completar cuadro de composición corporal |

---

## 8. Estructura de archivos sugerida para Claude Code

```
runner-agent/
├── .env                        # Credenciales (Garmin, Scopus, WoS, Claude API) — NO versionar
├── .gitignore
├── README.md
├── requirements.txt
│
├── data/
│   ├── garmin_client.py        # Wrapper sobre python-garminconnect
│   ├── scopus_client.py        # Cliente Scopus API
│   └── wos_client.py           # Cliente Web of Science API
│
├── agents/
│   ├── orchestrator.py         # Agente principal — coordina sub-agentes
│   ├── technique_agent.py      # Análisis técnica de carrera
│   ├── fatigue_agent.py        # HRV, Body Battery, ACWR
│   ├── plan_agent.py           # Generación de plan adaptativo
│   ├── science_agent.py        # Búsqueda y cita de papers
│   └── nutrition_agent.py      # Balance calórico y composición corporal
│
├── memory/
│   ├── runner_profile.py       # Perfil persistente del corredor
│   └── db.py                   # SQLite schema y operaciones
│
├── scheduler/
│   └── daily_check.py          # Revisión automática matutina
│
└── reports/
    └── weekly_report.py        # Generador de reporte semanal
```

---

## 9. Variables de entorno necesarias (.env)

```env
# Garmin (para python-garminconnect)
GARMIN_EMAIL=tu@email.com
GARMIN_PASSWORD=tu_password

# Scopus
SCOPUS_API_KEY=be95e1a10419abb49ff45df167a7996e

# Web of Science
WOS_API_KEY=d4dc882df6de02f8b35b85c92cf8f287929eacdc

# Claude / Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Base de datos
DATABASE_URL=sqlite:///runner_agent.db
```

---

## 10. Primer sprint — qué construir primero

1. **`garmin_client.py`** — conectar y descargar: HRV, Body Battery, última actividad de carrera con métricas de running dynamics.
2. **`runner_profile.py`** — schema SQLite con perfil del corredor, baseline HRV, historial de lesiones y metas.
3. **`fatigue_agent.py`** — lógica de análisis HRV vs baseline + cálculo ACWR básico.
4. **`science_agent.py`** — tool de búsqueda en Scopus por keyword, retorna abstract + cita formateada.
5. **`orchestrator.py`** — integrar los anteriores en un agente Claude que genere el reporte diario.

Validar con datos reales del usuario antes de agregar más sub-agentes.

---

## 11. Consideraciones clave

- **Baseline personal, no poblacional.** El HRV "normal" de José no es el promedio de la literatura. El agente debe construir el baseline de cada corredor en las primeras 2–3 semanas antes de hacer recomendaciones de carga.
- **No reemplaza al médico deportivo.** El agente detecta patrones y alerta; las decisiones médicas (lesiones, condiciones subyacentes) requieren profesional humano.
- **Privacidad de datos.** Las credenciales de Garmin dan acceso a datos muy sensibles de salud. Diseñar desde el inicio con seguridad: `.env` local, nunca en el repo, considerar cifrado en base de datos.
- **El diferenciador del producto** es la combinación de tres cosas que ninguna app hace juntas: datos biomecánicos reales + ajuste semanal basado en respuesta individual + respaldo en literatura científica con cita específica.
