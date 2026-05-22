## ADDED Requirements

### Requirement: Ciclo diario al despertar
El sistema SHALL ejecutar automáticamente cada mañana (hora configurable) un análisis que: lea HRV + Body Battery del día, calcule ACWR actual, genere recomendación de tipo de día y ajuste el entrenamiento del día si corresponde.

#### Scenario: Ejecución matutina completa
- **WHEN** el scheduler dispara el ciclo diario
- **THEN** el orquestador invoca secuencialmente: `garmin_client.get_daily_health()` → `fatigue_agent.analyze()` → `plan_agent.adjust_today()` → imprime reporte al corredor

#### Scenario: Datos de Garmin no disponibles (reloj sin sincronizar)
- **WHEN** el reloj Garmin no sincronizó datos desde anoche
- **THEN** el sistema advierte "Sin datos de Garmin para hoy" y muestra el plan del día sin ajuste por HRV

### Requirement: Ciclo post-entrenamiento
El sistema SHALL analizar la sesión de carrera más reciente dentro de la hora posterior a su registro en Garmin: métricas de técnica vs objetivos, degradación de forma, y actualización del ACWR.

#### Scenario: Análisis post-sesión
- **WHEN** se detecta una nueva actividad de carrera en Garmin
- **THEN** el orquestador invoca: `technique_agent.analyze_session()` → `fatigue_agent.update_acwr()` → genera resumen de la sesión

### Requirement: Revisión semanal (lunes)
El sistema SHALL ejecutar cada lunes una revisión completa que: descargue los datos de la semana anterior, compare plan vs ejecución, analice tendencias de HRV y técnica, consulte literatura científica si detecta patrones significativos, y genere el plan de la semana siguiente con reporte completo.

#### Scenario: Revisión semanal con patrón de asimetría detectado
- **WHEN** la revisión semanal detecta que el balance GCT izq/der superó 52/48 en ≥ 3 sesiones
- **THEN** el orquestador invoca `science_agent.search()` con query sobre asimetría de carrera y lesiones, incluye la cita en el reporte semanal y añade ejercicios de corrección al plan

#### Scenario: Revisión semanal sin acceso a APIs científicas
- **WHEN** Scopus o WoS no responden (rate limit o error de red)
- **THEN** el reporte semanal se genera igualmente sin citas científicas, con nota de que la evidencia no pudo recuperarse

### Requirement: Respaldo científico de recomendaciones clave
El sistema SHALL incluir al menos una cita de Scopus o WoS para cada recomendación de cambio de técnica, ajuste de volumen > 20% o alerta de lesión — citando: autor(es), revista, año y hallazgo clave.

#### Scenario: Cita incluida en recomendación
- **WHEN** el agente recomienda aumentar cadencia a 175 spm
- **THEN** el reporte incluye: "Basado en: Heiderscheit et al. (2011) Journal of Orthopaedic & Sports Physical Therapy — aumentar cadencia 5–10% reduce la carga articular en rodilla y cadera"
