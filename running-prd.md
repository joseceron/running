# Running Agent — PRD de Capacidades y Datos

**Versión:** 1.0 | **Fecha:** 2026-05-12 | **Estado:** Sistema funcionando, datos reales en producción

---

## 1. Qué es el sistema

Agente de IA personal que se conecta a Garmin Connect, descarga métricas fisiológicas reales y las combina con literatura científica peer-reviewed (Scopus + Web of Science) para generar recomendaciones de entrenamiento y salud individualizadas. No usa valores poblacionales; construye el baseline personal de cada usuario en las primeras semanas.

**Stack:** Python 3.11, Claude `claude-sonnet-4-6` (Anthropic API), `python-garminconnect`, SQLite, Scopus API, Web of Science API.

**Repo:** `/Users/jose.ceron/Documents/dev/running/runner-agent/`
**Ejecutar:** `cd runner-agent && .venv/bin/python main.py daily`

---

## 2. Fuentes de datos — todo lo que se recopila hoy

### 2.1 Datos fisiológicos diarios (Garmin Connect)

| Dato | API Garmin | Frecuencia | Relevancia de salud |
|------|-----------|------------|---------------------|
| **HRV RMSSD nocturno** | `get_hrv_data()` | Por noche | Sistema nervioso autónomo, recuperación, estrés crónico |
| **Body Battery** | `get_body_battery()` | Continuo (5 min) | Energía disponible estimada; proxy de recuperación |
| **FC en reposo** | `get_stats()` | Diario | Fitness cardiovascular, sobrentrenamiento, enfermedad |
| **SpO₂ promedio** | `get_spo2_data()` | Nocturno | Calidad de oxigenación, apnea del sueño latente |
| **Puntuación de sueño** | `get_sleep_data()` | Por noche | Calidad global del sueño |
| **Sueño profundo (seg)** | `get_sleep_data()` | Por noche | Restauración física, síntesis proteica, reparación muscular |
| **Sueño REM (seg)** | `get_sleep_data()` | Por noche | Consolidación de memoria, regulación emocional |
| **Sueño ligero (seg)** | `get_sleep_data()` | Por noche | Composición del ciclo de sueño |
| **Nivel de estrés promedio** | `get_stats()` | Diario | Estrés fisiológico acumulado (basado en HRV continuo) |
| **VO₂Max estimado** | `get_stats()` | Semanal | Marcador de longevidad cardiovascular |

### 2.2 Running Dynamics (por actividad de carrera)

| Dato | Campo Garmin | Relevancia de salud / lesión |
|------|-------------|------------------------------|
| **Cadencia promedio** | `averageRunningCadenceInStepsPerMinute` | < 170 spm asociado a mayor impacto y lesiones de rodilla/sóleo |
| **Oscilación vertical (cm)** | `directVerticalOscillation` | Ineficiencia biomecánica; mayor gasto energético |
| **Vertical Ratio (%)** | `directVerticalRatio` | Economía de carrera; proxy de lesiones por impacto repetitivo |
| **Ground Contact Time (ms)** | `directGroundContactTime` | Tiempo de carga por pisada; mayor GCT → más estrés articular |
| **Balance GCT izq/der (%)** | `directGroundContactBalance` | **Asimetría de carga bilateral** — precursor directo de lesión por compensación |
| **Longitud de zancada (m)** | `directStrideLength` | Overstride detectado cuando zancada larga + cadencia baja |
| **FC promedio y por km** | `averageHR`, splits | Distribución de zonas, sobreesfuerzo |
| **Tiempo en zonas FC** | `get_activity_hr_in_timezones()` | Diagnóstico de polarización del entrenamiento |
| **Splits por km** | `get_activity_splits()` | Degradación de forma durante la sesión |
| **Distancia y duración** | `distance`, `duration` | Volumen de carga semanal |

### 2.3 Historial y perfil del corredor (SQLite)

| Tabla | Datos almacenados |
|-------|------------------|
| `runner_profile` | Nombre, edad, peso, talla, FCmáx, FC reposo, meta, fecha inicio sistema |
| `hrv_log` | Fecha + HRV RMSSD por noche (baseline personal en construcción) |
| `weekly_history` | Semana, km planeados, km ejecutados, HRV promedio, Body Battery promedio, ACWR, notas del agente |
| `body_weight_history` | Peso con timestamp (tendencia de composición corporal) |
| `nutrition_log` | Fecha, kcal ingeridas, proteína (g), estado |
| Registro de lesiones | Tipo, fecha, severidad, notas de recuperación (como entrada especial en `weekly_history`) |

---

## 3. Qué analiza el sistema hoy

### 3.1 Sub-agente de Fatiga y Carga (`fatigue_agent.py`)

- **HRV vs baseline personal:** clasifica el día en `optimal` / `reduced` / `suppressed` comparando el HRV nocturno contra la media móvil de 7 días de los últimos 14 registros (no contra tablas poblacionales).
- **ACWR (Acute:Chronic Workload Ratio):** ratio carga de los últimos 7 días vs promedio de las últimas 4 semanas. Alerta en ACWR > 1.5 (zona de riesgo de lesión documentada en literatura).
- **Body Battery:** alerta de descanso si cae < 40.
- **Recomendación del día:** `load` / `active_recovery` / `rest` con justificación de cada alerta.

### 3.2 Sub-agente de Técnica (`technique_agent.py`)

- Evalúa cadencia contra objetivo 170–180 spm.
- Detecta asimetría GCT izq/der > 52/48 (compensación o lesión latente).
- Detecta degradación de forma intrasesión comparando primeros vs últimos 3 km (caída de cadencia > 5% o aumento de oscilación > 10%).
- Tendencia semanal de técnica: compara promedios semana actual vs semana anterior.

### 3.3 Sub-agente de Nutrición (`nutrition_agent.py`)

- BMR calculado con **Mifflin-St Jeor** usando datos reales de peso/talla/edad del perfil.
- Balance calórico: `ingesta - (BMR + calorías activas Garmin)`.
- **Alerta de déficit crónico:** si balance < -500 kcal por 3+ días consecutivos → riesgo de pérdida de masa muscular.
- **Alerta de proteína:** en días con > 15 km corridos, verifica ingesta ≥ 1.6 g/kg de peso.

### 3.4 Sub-agente de Evidencia Científica (`science_agent.py`)

- Busca papers en Scopus (`TITLE-ABS-KEY`) y Web of Science cuando el agente detecta una alerta que requiere justificación.
- Retorna abstract + cita formateada (autor, año, DOI).
- Temas cubiertos: cadencia e injury prevention, HRV y training load, ACWR y overuse injuries, sleep y athletic recovery, running economy.

### 3.5 Orquestador (`orchestrator.py`)

Tres modos de ejecución coordinados por Claude (tool use):

| Modo | Trigger | Contenido |
|------|---------|-----------|
| **`daily`** (matutino) | `main.py daily` | HRV del día + Body Battery + ACWR + recomendación + alertas + frase motivadora |
| **`post-run`** | `main.py post_run` | Análisis de última sesión: técnica + carga + alertas de lesión |
| **`weekly`** | `main.py weekly` | Revisión semanal + plan 7 días + nutrición + evidencia científica |

---

## 4. Datos de salud capturados — potencial más allá del deporte

El sistema captura datos que van mucho más allá del rendimiento deportivo. Esto es lo que cada señal revela sobre la salud general:

### 4.1 Sistema Nervioso Autónomo (HRV)

El HRV nocturno RMSSD es el marcador fisiológico más sensible del estado del SNA. Valores crónicamente bajos o en declive sostenido pueden indicar:

- **Estrés crónico acumulado** (laboral, emocional, físico) — el SNA simpático dominante suprime el parasimpático.
- **Sobreentrenamiento subclínico** — antes de que aparezcan síntomas subjetivos.
- **Infección / inflamación incipiente** — el HRV cae 24–48h antes de que los síntomas sean visibles.
- **Calidad de recuperación nocturna** — el HRV es el marcador proximal de cuánto se restauró el organismo durante el sueño.
- **Tendencias de adaptación al entrenamiento** — un corredor que se adapta bien muestra HRV estable o en aumento con el tiempo.

**Potencial de alerta de salud:** un descenso de HRV > 15% del baseline personal durante 3+ días sin explicación deportiva es una señal de investigar causas sistémicas (enfermedad, déficit de sueño, estrés crónico).

### 4.2 SpO₂ nocturno

El sistema ya captura el SpO₂ promedio nocturno de Garmin. Esto es clave para:

- **Screening de apnea obstructiva del sueño** — caídas repetidas de SpO₂ < 90% durante el sueño son el patrón diagnóstico principal.
- **Monitoreo de salud respiratoria** — valores crónicamente bajos (< 95%) en reposo nocturno merecen evaluación médica.
- **Altitud y aclimatación** — si el usuario entrena o viaja a altitud, el SpO₂ nocturno detecta hipoxemia antes de que sea sintomática.

**Dato actual del sistema:** el campo `spo2_avg` ya está en `get_daily_health()` y se almacenaría en SQLite con una migración mínima de la tabla `hrv_log`.

### 4.3 Arquitectura del sueño (profundo, REM, ligero)

El sistema descarga los segundos de cada fase de sueño. La composición del sueño es un biomarcador de:

- **Recuperación muscular:** el sueño profundo (N3) es cuando se libera hormona de crecimiento y se sintetiza proteína. Un corredor con < 90 min de sueño profundo crónico tiene recuperación deteriorada aunque duerma 8h.
- **Salud cognitiva:** el REM es crítico para consolidación de memoria y regulación emocional. Déficit crónico de REM está asociado a deterioro cognitivo a largo plazo.
- **Efecto del alcohol:** el alcohol destruye el REM de manera característica y detectable en los datos.
- **Jet lag y turnos de trabajo:** alteran la arquitectura del sueño de manera específica y trazable.
- **Envejecimiento:** la proporción de sueño profundo disminuye con la edad; el sistema puede trackear esta tendencia.

### 4.4 FC en reposo — tendencia

La FC en reposo es el marcador más clásico de fitness cardiovascular, pero su valor real está en la **tendencia temporal**, no en un punto aislado. El sistema ya guarda el perfil con `resting_hr` y podría agregar un log histórico para detectar:

- **Sobrentrenamiento:** FC reposo sube 5–7 lpm sobre el baseline personal.
- **Enfermedad inminente:** subida aguda de 8–10 lpm, especialmente combinada con caída de HRV.
- **Mejora de condición física:** descenso gradual de FC reposo es la señal más clara de adaptación aeróbica.
- **Deshidratación crónica:** eleva FC reposo de forma sostenida.

### 4.5 Nivel de estrés Garmin (HRV intradía)

El índice de estrés de Garmin es una estimación continua basada en la variabilidad del intervalo RR durante las horas de vigilia. El sistema ya captura `stress_avg`. Esto revela:

- **Carga alostática acumulada** — suma de estrés fisiológico del día, independientemente de la percepción subjetiva.
- **Respuesta al ejercicio vs al estrés cotidiano** — el pico de estrés en una sesión dura es esperable; picos altos en reposo son la señal de alarma.
- **Efecto de prácticas de recuperación** — meditación, respiración diafragmática, etc., reducen el estrés Garmin de forma medible.

### 4.6 Body Battery — proxy de energía vital

El Body Battery integra HRV, estrés, sueño y actividad en un score 0–100. Más allá del deporte, es una proxy de:

- **Deuda de sueño acumulada** — valores que no suben de 60–70 tras dormir indican sueño insuficiente o de mala calidad.
- **Capacidad de carga laboral** — un usuario que comienza el día con Body Battery < 50 sistemáticamente está en estado de deuda crónica de recuperación.
- **Efecto de estresores extradepórtivos** — una semana de alta carga laboral se ve en el Body Battery aunque no se entrene.

### 4.7 Biomecánica — asimetría y lesión latente

La asimetría GCT izq/der es la señal biomecánica más directamente ligada a salud musculoesquelética:

- **Compensación activa:** cuando un lado del cuerpo tiene una disfunción (debilidad, dolor, rigidez), el otro lado absorbe más carga. Esto aparece en el balance GCT antes de que el corredor lo perciba conscientemente.
- **Detección de recaída de lesión:** en el caso de José, un aumento del balance hacia el lado del sóleo lesionado es una señal de alarma temprana.
- **Disfunción de cadera/tobillo:** asimetrías persistentes de GCT pueden reflejar problemas en la cadena cinética que no están en el punto de dolor.

### 4.8 Peso corporal (tendencia)

El sistema ya tiene `body_weight_history` con timestamps. La tendencia de peso combinada con datos de entrenamiento y nutrición revela:

- **Composición corporal:** si el peso baja mientras la FC reposo sube y el HRV cae, es pérdida de masa muscular, no grasa.
- **Retención de agua post-entrenamiento:** fluctuaciones de 1–2 kg son normales post-carrera larga; retención persistente puede indicar inflamación crónica.
- **Déficit calórico crónico:** el sistema ya lo detecta, pero el peso lo confirma objetivamente.

---

## 5. Datos que Garmin tiene disponibles y el sistema AÚN NO captura

Estos están accesibles vía `python-garminconnect` con cambios mínimos al código:

| Dato | Método API | Valor de salud |
|------|-----------|----------------|
| **Temperatura cutánea nocturna** | `get_skin_temperature_data()` | Ciclo menstrual, enfermedades febriles, ovulación |
| **Pasos y sedentarismo** | `get_steps_data()` | Actividad total diaria, horas sedentarias consecutivas |
| **Hidratación** | `get_hydration_data()` | Déficit de hidratación crónico |
| **Ciclo menstrual** | `get_menstrual_data()` | Correlación con HRV y rendimiento |
| **Respiración** | `get_respiration_data()` | Frecuencia respiratoria en reposo nocturno — marcador de apnea e infección |
| **FC en tiempo real** | `get_heart_rates(date)` | Perfil intradía de FC; picos en reposo = estrés o arritmia |
| **Tiempo sentado vs activo** | `get_intensity_minutes_data()` | Carga sedentaria, minutos de actividad intensa semanal |
| **Pulso de oxígeno durante sueño** | dentro de `get_sleep_data()` | Episodios de desaturación; screening de apnea |
| **Resumen calórico Garmin** | `get_stats()` → `activeKilocalories` | Gasto energético real por actividad (actualmente inyectado manualmente) |

---

## 6. Potencial de expansión hacia salud integral

### 6.1 Monitor de Sistema Nervioso Autónomo

El sistema ya tiene la infraestructura para hacer lo que los wearables de bienestar ofrecen como producto principal: un dashboard del SNA que combina HRV nocturno + estrés intradía + Body Battery + sueño en un score de "capacidad del sistema nervioso" para el día.

**Implementación estimada:** 1–2 días. Los datos ya se descargan; falta un `calculate_autonomic_score()` que los pondere.

### 6.2 Screening de apnea del sueño

Con SpO₂ nocturno + frecuencia respiratoria nocturna + arquitectura de sueño, el sistema puede detectar el patrón de apnea (desaturaciones repetidas + sueño fragmentado + REM reducido) y sugerir consulta médica. No es diagnóstico, pero sí screening.

**Dato clave:** el 80% de las apneas del sueño no están diagnosticadas. Garmin ya mide esto.

### 6.3 Correlación estrés-rendimiento

Con `stress_avg` diario + HRV + Body Battery + rendimiento en la sesión (pace, FC al mismo pace), el sistema puede modelar cómo el estrés extradepórtivo impacta el rendimiento físico del usuario específico. Esto cierra el loop entre salud mental/estrés laboral y salud física.

### 6.4 Alerta de enfermedad incipiente

Patrón típico de enfermedad antes de síntomas:
1. HRV cae > 15% del baseline
2. FC reposo sube > 5 lpm
3. Body Battery no se recupera con el sueño habitual
4. Temperatura cutánea sube ligeramente

El sistema puede detectar este patrón multimodal 24–48h antes de que el usuario se sienta enfermo, y recomendar reducir carga o descansar profilácticamente.

### 6.5 Seguimiento de composición corporal

Combinando `body_weight_history` + nutrición (`kcal`, `protein_g`) + gasto calórico Garmin + VO₂Max tendencia, el sistema puede estimar si los cambios de peso son grasa o músculo, y alertar cuando la pérdida de peso sugiere catabolismo muscular.

### 6.6 Longevidad y salud cardiovascular

VO₂Max es el predictor de mortalidad cardiovascular más robusto que existe. El sistema ya lo captura. Con datos longitudinales de 6–12 meses se puede:
- Trazar la trayectoria de VO₂Max del usuario.
- Comparar con percentiles por edad/sexo.
- Correlacionar qué intervenciones (más volumen, más sueño, menos estrés) lo mejoran.

---

## 7. Arquitectura técnica del sistema

```
runner-agent/
├── main.py                      # Punto de entrada: daily / post_run / weekly / schedule
├── data/
│   ├── garmin_client.py         # GarminConnectClient — wrapper sobre python-garminconnect
│   ├── scopus_client.py         # ScopusClient — búsqueda TITLE-ABS-KEY, rate 1s
│   └── wos_client.py            # WoSClient — Web of Science Starter API
├── agents/
│   ├── orchestrator.py          # Agente Claude principal — coordina vía tool use
│   ├── technique_agent.py       # Cadencia, GCT, asimetría, degradación de forma
│   ├── fatigue_agent.py         # HRV vs baseline, ACWR, recomendación del día
│   ├── plan_agent.py            # Plan semanal adaptativo con ritmos personalizados
│   ├── science_agent.py         # Búsqueda Scopus/WoS — cita formateada con DOI
│   └── nutrition_agent.py       # BMR Mifflin-St Jeor, balance calórico, alerta proteína
├── memory/
│   ├── runner_profile.py        # CRUD perfil, baseline HRV, historial lesiones
│   └── db.py                    # SQLite schema: runner_profile, hrv_log, weekly_history,
│                                #   body_weight_history, nutrition_log
├── reports/
│   └── weekly_report.py         # Generador HTML
└── output/                      # HTML generados: reportes diarios, diagnóstico, nutrición
```

### Persistencia (actual → futuro)
- **Fase 1 (actual):** SQLite local en `runner_agent.db`
- **Fase 2 (planificada):** Firebase Realtime Database (sync multi-dispositivo)

### Flujo de una ejecución `daily`
1. Claude recibe el prompt del día con el perfil del corredor.
2. Llama `get_daily_health(today)` → Garmin descarga HRV + BB + FC reposo + SpO₂ + sueño.
3. Llama `analyze_fatigue(today, body_battery)` → compara HRV vs baseline, calcula ACWR.
4. Si hay alertas críticas (HRV suprimido, ACWR > 1.5) → llama `find_scientific_evidence(topic)`.
5. Opcionalmente: `get_nutrition_status()` si hay datos de ingesta.
6. Claude genera el reporte final en texto estructurado.

---

## 8. Estado actual del sistema (2026-05-12)

| Componente | Estado |
|-----------|--------|
| Conexión Garmin | ✅ Funcionando con token cache |
| Descarga datos diarios | ✅ HRV, Body Battery, sueño, FC reposo, SpO₂ |
| Running dynamics | ✅ 17 sesiones descargadas y en SQLite desde dic 2025 |
| Análisis de fatiga | ✅ ACWR calculado; HRV en espera de baseline (0/14 noches) |
| Análisis de técnica | ✅ Diagnóstico real: 80% sesiones Z4-Z5 documentado |
| Nutrición | ✅ BMR calculado (1597.5 kcal/día), alerta proteína activa |
| Evidencia científica | ✅ Scopus + WoS conectados |
| Reporte diario HTML | ✅ Generado en `output/` |
| Baseline HRV personal | ⏳ En construcción (requiere 14 noches con reloj) |
| Scheduler automático | ⏳ Pendiente de activar como cron |
| Firebase | ⏳ Planificado Fase 2 |

### Hallazgo diagnóstico real
El análisis de las 17 sesiones históricas reveló que el **80% de las sesiones se corrieron en Z4–Z5** (FC 164–190 lpm). El objetivo de entrenamiento polarizado es 80% en Z1-Z2. Esta inversión de zonas es la causa probable del desgarro de sóleo del 49% (enero 2024). El agente está diseñado para corregir esto progresivamente con ritmos personalizados basados en zonas reales.

---

## 9. APIs externas y credenciales

Las credenciales reales están en `runner-agent/.env` (no versionar).

| Variable | Servicio | Notas |
|---------|---------|-------|
| `GARMIN_EMAIL` / `GARMIN_PASSWORD` | Garmin Connect | Acceso vía `python-garminconnect`; tokens cacheados |
| `ANTHROPIC_API_KEY` | Claude API | Modelo: `claude-sonnet-4-6` |
| `SCOPUS_API_KEY` | Scopus (Elsevier) | Header `X-ELS-APIKey`; rate limit 1 req/seg |
| `WOS_API_KEY` | Web of Science | Header `X-ApiKey`; plan Free Institutional Member |
| `DATABASE_URL` | SQLite | `sqlite:///runner_agent.db` |

---

## 10. Principios de diseño

1. **Baseline personal, no poblacional.** El sistema aprende al usuario durante las primeras 2–3 semanas antes de hacer recomendaciones de carga. No usa tablas de "HRV normal para hombre de 30 años".

2. **El agente detecta y alerta; no reemplaza al médico.** Toda señal de salud se presenta como "esto merece atención", no como diagnóstico.

3. **Privacidad.** Datos de salud muy sensibles. Las credenciales Garmin dan acceso completo a datos fisiológicos continuos. Nunca al repo. Considerar cifrado en la DB en Fase 2.

4. **Evidencia con cita.** Toda recomendación que cambie el plan > 20% o que tenga impacto en salud va acompañada de un paper con DOI. No "la ciencia dice" sino "Haugen et al., 2014, IJSPP: cadencia ≥ 170 spm reduce carga en rodilla un 14%".

5. **Datos reales propios primero.** Validar con datos del usuario concreto antes de escalar o generalizar.
