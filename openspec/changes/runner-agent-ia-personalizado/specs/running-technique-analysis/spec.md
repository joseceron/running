## ADDED Requirements

### Requirement: Análisis de métricas de biomecánica por sesión
El sistema SHALL analizar para cada actividad de carrera: cadencia (objetivo: 170–180 spm), oscilación vertical (menor es mejor), Vertical Ratio (indicador de economía), GCT promedio y balance GCT izq/der (asimetría > 52/48 = alerta).

#### Scenario: Cadencia por debajo del rango óptimo
- **WHEN** la cadencia promedio de la sesión es menor a 170 spm
- **THEN** el sistema señala la cadencia como área de mejora e incluye el diferencial respecto al objetivo

#### Scenario: Asimetría de GCT detectada
- **WHEN** el balance GCT supera la proporción 52/48 (cualquier lado)
- **THEN** el sistema emite alerta de asimetría con el valor exacto y la nota de posible compensación o lesión latente

### Requirement: Detección de degradación de forma durante la actividad
El sistema SHALL detectar degradación de forma comparando las métricas de los primeros vs últimos kilómetros de la sesión: una caída de cadencia ≥ 5% o aumento de oscilación vertical ≥ 10% indica fatiga de forma.

#### Scenario: Degradación de cadencia detectada
- **WHEN** la cadencia promedio de los últimos 3 km es ≥ 5% menor que los primeros 3 km
- **THEN** el sistema reporta "degradación de forma detectada en km N" con el porcentaje de caída

#### Scenario: Forma mantenida durante toda la sesión
- **WHEN** cadencia y oscilación vertical se mantienen estables (< 5% de variación) a lo largo de la sesión
- **THEN** el sistema reporta "forma técnica mantenida" como indicador positivo

### Requirement: Tendencia semanal de técnica
El sistema SHALL calcular la tendencia de cada métrica de running dynamics comparando el promedio de la semana actual vs la semana anterior para detectar mejoras o deterioros sistemáticos.

#### Scenario: Mejora sostenida de cadencia
- **WHEN** la cadencia promedio semanal aumenta ≥ 3 spm respecto a la semana anterior
- **THEN** el sistema registra la mejora en el historial y la destaca en el reporte semanal

#### Scenario: Deterioro de Vertical Ratio
- **WHEN** el Vertical Ratio semanal promedio aumenta ≥ 0.5 puntos porcentuales
- **THEN** el sistema señala deterioro de economía de carrera y sugiere revisión de técnica
