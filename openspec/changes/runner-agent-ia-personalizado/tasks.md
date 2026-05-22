## 1. Infraestructura base

- [x] 1.1 Crear estructura de directorios: `runner-agent/data/`, `agents/`, `memory/`, `scheduler/`, `reports/`
- [x] 1.2 Crear `requirements.txt` con: `garminconnect`, `anthropic`, `requests`, `python-dotenv`, `apscheduler`
- [x] 1.3 Crear `.gitignore` con `.env`, `*.db`, `__pycache__/`, `.venv/`
- [x] 1.4 Crear `.env` local con estructura de variables (sin valores reales) y apuntar al archivo de referencia en `/Users/jose.ceron/Documents/emira/.env`
- [x] 1.5 Instalar dependencias en entorno virtual: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

## 2. Capa de datos — Garmin

- [x] 2.1 Implementar `data/garmin_client.py`: clase `GarminConnectClient` con autenticación via variables de entorno
- [x] 2.2 Implementar método `get_daily_health(date)`: retorna HRV, Body Battery, FC en reposo, SpO₂, sueño, estrés, VO₂Max
- [x] 2.3 Implementar método `get_last_run_dynamics()`: retorna cadencia, oscilación vertical, Vertical Ratio, GCT, balance GCT, longitud de zancada, splits, zonas FC
- [x] 2.4 Implementar método `get_hrv_history(days=14)`: retorna lista de registros HRV nocturnos
- [ ] 2.5 Probar los 3 métodos con datos reales del usuario — verificar que los campos retornan valores correctos

## 3. Persistencia — Perfil del corredor

- [x] 3.1 Implementar `memory/db.py`: función `get_connection()` que lee `DATABASE_URL` del entorno
- [x] 3.2 Crear schema SQLite en `memory/db.py`: tablas `runner_profile`, `body_weight_history`, `hrv_log`, `weekly_history`, `nutrition_log`, `science_cache`
- [x] 3.3 Implementar `memory/runner_profile.py`: funciones `create_profile()`, `get_profile()`, `update_weight()`, `add_injury()`, `set_goal()`
- [x] 3.4 Implementar `get_hrv_baseline()`: media móvil 7 días sobre últimos 14 registros; retorna `None` si hay < 14 días
- [x] 3.5 Implementar `save_weekly_summary()` y `get_weekly_history(n_weeks)` para persistir revisiones semanales
- [x] 3.6 Ejecutar script de inicialización con datos reales de José: crear perfil, ingresar historial de lesión del sóleo, establecer meta

## 4. Sub-agente: Fatiga y Carga

- [x] 4.1 Implementar `agents/fatigue_agent.py`: función `analyze_day(date)` que retorna estado HRV (`optimal`/`reduced`/`suppressed`) y recomendación del día (`load`/`active_recovery`/`rest`)
- [x] 4.2 Implementar cálculo de ACWR: carga aguda (7 días) / carga crónica (28 días promedio); definir proxy de carga
- [x] 4.3 Implementar alerta de ACWR > 1.5 con mensaje descriptivo
- [x] 4.4 Implementar `update_acwr(activity)`: actualiza ACWR tras registrar nueva sesión
- [ ] 4.5 Probar con 4 semanas de datos reales de Garmin: validar que los valores de ACWR son coherentes con el historial de entrenamiento

## 5. Sub-agente: Técnica de Carrera

- [x] 5.1 Implementar `agents/technique_agent.py`: función `analyze_session(activity)` que retorna evaluación de cadencia, oscilación vertical, GCT y balance
- [x] 5.2 Implementar detección de degradación de forma: comparar primeros vs últimos 3 km de la sesión (cadencia, oscilación)
- [x] 5.3 Implementar alerta de asimetría GCT > 52/48 con valor exacto
- [x] 5.4 Implementar `get_weekly_technique_trend()`: compara promedios semana actual vs semana anterior para cada métrica
- [ ] 5.5 Probar con datos reales de las últimas 5 sesiones de carrera del usuario

## 6. Sub-agente: Evidencia Científica

- [x] 6.1 Implementar `data/scopus_client.py`: función `search(query, max_results=5)` con rate limiting de 1 seg y caché SQLite (TTL 7 días)
- [x] 6.2 Implementar `data/wos_client.py`: función `search(query, max_results=5)` con rate limiting de 1 req/seg y caché SQLite
- [x] 6.3 Implementar `agents/science_agent.py`: función `find_evidence(topic)` que construye la query apropiada, consulta Scopus y WoS, y retorna papers clasificados por nivel de evidencia (`strong`/`moderate`/`weak`)
- [x] 6.4 Implementar función `format_citation(paper)`: retorna string con "Autor (año) Revista — hallazgo clave"
- [ ] 6.5 Probar con las 4 queries de ejemplo del resumen (cadencia + lesiones, oscilación vertical, HRV + carga, nutrición + running)

## 7. Sub-agente: Plan Adaptativo

- [x] 7.1 Implementar `agents/plan_agent.py`: función `generate_weekly_plan(runner_data)` que genera plan de 7 días basado en ACWR actual, HRV de la semana y ejecución de la semana anterior
- [x] 7.2 Implementar cálculo de zonas FC personales del corredor a partir de FC máxima y FC en reposo
- [x] 7.3 Implementar `calculate_daily_pace(zone, hrv_state)`: retorna ritmo en min/km personalizado para el estado del día
- [x] 7.4 Implementar validación de distribución 80/20: verifica distribución de intensidad de la semana anterior y ajusta la siguiente
- [x] 7.5 Implementar `adjust_today(plan, daily_health)`: ajusta el entrenamiento del día según HRV y Body Battery matutinos

## 8. Sub-agente: Nutrición

- [x] 8.1 Implementar `agents/nutrition_agent.py`: función `log_intake(kcal, protein_g)` que persiste la ingesta del día
- [x] 8.2 Implementar `calculate_daily_balance(date)`: gasto Garmin (BMR + calorías activas) - ingesta; retorna balance en kcal
- [x] 8.3 Implementar detección de déficit calórico crónico: alerta si balance < -500 kcal por 3+ días consecutivos
- [x] 8.4 Implementar alerta de proteína insuficiente: < 1.6g/kg en días con > 15 km corridos

## 9. Orquestador principal

- [x] 9.1 Implementar `agents/orchestrator.py` con el Anthropic Agent SDK: agente Claude (`claude-sonnet-4-6`) con tools que invocan cada sub-agente
- [x] 9.2 Implementar ciclo diario: `daily_morning_check()` — HRV + Body Battery → ACWR → recomendación del día → ajuste del plan
- [x] 9.3 Implementar ciclo post-entrenamiento: `post_run_analysis()` — técnica → actualizar ACWR → resumen de sesión
- [x] 9.4 Implementar ciclo semanal: `weekly_review()` — descargar semana → comparar plan/ejecución → tendencias → evidencia científica si hay patrones → generar plan siguiente
- [x] 9.5 Implementar lógica de respaldo científico: para recomendaciones de cambio de técnica, ajuste de volumen > 20% o alertas de lesión, invocar `science_agent` y agregar cita al reporte

## 10. Scheduler y reportes

- [x] 10.1 Implementar `scheduler/daily_check.py`: configurar APScheduler para ejecutar `daily_morning_check()` a hora configurable (variable `MORNING_CHECK_TIME` en `.env`)
- [x] 10.2 Implementar `reports/weekly_report.py`: formatea el reporte semanal en texto legible con secciones: resumen de semana, alertas, plan siguiente, evidencia científica
- [x] 10.3 Crear script `main.py` en la raíz que inicia el scheduler y expone comandos CLI: `python main.py daily`, `python main.py weekly`, `python main.py post-run`
- [ ] 10.4 Probar el ciclo completo end-to-end con datos reales: ejecutar `daily`, registrar una actividad, ejecutar `post-run`, ejecutar `weekly`

## 11. Validación final

- [x] 11.1 Verificar que ninguna credencial aparece en el código fuente (grep por el email de Garmin, API keys)
- [x] 11.2 Verificar que el sistema emite advertencia correcta cuando el baseline HRV tiene < 14 días
- [x] 11.3 Verificar que el ACWR se calcula correctamente con 4+ semanas de historial real
- [x] 11.4 Verificar que las citas de Scopus/WoS incluyen nivel de evidencia en el reporte
- [x] 11.5 Documentar en README.md: instalación, configuración del `.env`, primeros pasos, y cómo construir el baseline HRV inicial
