## ADDED Requirements

### Requirement: Plan semanal basado en datos reales de la semana anterior
El sistema SHALL generar cada lunes un plan de entrenamiento para los próximos 7 días usando: ejecución real de la semana anterior (vs plan propuesto), ACWR actual, estado de HRV y métricas de técnica de la última sesión.

#### Scenario: Semana anterior ejecutada según plan
- **WHEN** el corredor completó ≥ 80% del volumen planificado y el ACWR es ≤ 1.3
- **THEN** el plan siguiente mantiene o incrementa el volumen en ≤ 10% (regla del 10%)

#### Scenario: Semana anterior con sub-ejecución
- **WHEN** el corredor completó < 70% del volumen planificado
- **THEN** el plan siguiente ajusta el volumen a la carga real ejecutada antes de proponer incremento

### Requirement: Ritmos personalizados por zonas de FC reales
El sistema SHALL calcular los ritmos de entrenamiento del día usando las zonas de FC personales del corredor (Z1–Z5) derivadas de su FC máxima y FC en reposo actuales — no ritmos fijos genéricos.

#### Scenario: Ritmo de día Z2 con HRV reducido
- **WHEN** el plan del día indica un entrenamiento de base aeróbica (Z2) y el HRV del día es `reduced`
- **THEN** el ritmo se calcula para Z2 usando la FC real de ese día: "Corre a 5:48/km (tu Z2 hoy dado tu HRV reducido)" en lugar de "corre a 5:30/km"

#### Scenario: Entrenamiento de calidad con HRV óptimo
- **WHEN** el plan incluye series de velocidad y el estado del día es `load`
- **THEN** los ritmos de series se calculan al 90–95% de la FC máxima real del corredor

### Requirement: Distribución de intensidad polarizada
El sistema SHALL distribuir el volumen semanal siguiendo el modelo 80/20: ≥ 80% del tiempo en Z1–Z2 (baja intensidad) y ≤ 20% en Z4–Z5 (alta intensidad), salvo en semanas de carga o recuperación explícita.

#### Scenario: Distribución correcta al final de la semana
- **WHEN** se revisa la ejecución de la semana
- **THEN** el sistema valida que la distribución Z1-Z2 fue ≥ 75% del tiempo total de carrera

#### Scenario: Corrección por exceso de intensidad
- **WHEN** el corredor corrió > 25% del tiempo en Z3–Z5 la semana anterior
- **THEN** el plan siguiente prioriza explícitamente sesiones de Z1–Z2 y lo menciona en el reporte
