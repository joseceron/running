## ADDED Requirements

### Requirement: Análisis HRV vs baseline personal
El sistema SHALL comparar el HRV nocturno del día actual contra el baseline personal del corredor (no contra valores de literatura) y clasificar el estado en: `optimal` (HRV ≥ baseline), `reduced` (HRV entre 85–99% del baseline) o `suppressed` (HRV < 85% del baseline).

#### Scenario: HRV en estado óptimo
- **WHEN** el HRV del corredor está en o por encima de su baseline personal
- **THEN** el sistema clasifica el día como `optimal` y permite carga de entrenamiento normal

#### Scenario: HRV suprimido
- **WHEN** el HRV está por debajo del 85% del baseline personal
- **THEN** el sistema emite alerta de recuperación y recomienda día de recuperación activa o descanso

#### Scenario: Baseline no disponible
- **WHEN** el baseline HRV aún no está construido (< 14 días de datos)
- **THEN** el sistema NO emite recomendación de carga basada en HRV y advierte al corredor

### Requirement: Cálculo de Acute:Chronic Workload Ratio (ACWR)
El sistema SHALL calcular el ACWR como la razón entre la carga de las últimas 7 días (aguda) y el promedio de las últimas 4 semanas (crónica), usando como proxy de carga: distancia × intensidad_relativa_zona_FC.

#### Scenario: ACWR en zona segura
- **WHEN** el ACWR calculado está entre 0.8 y 1.3
- **THEN** el sistema indica zona de entrenamiento segura

#### Scenario: ACWR en zona de alerta
- **WHEN** el ACWR supera 1.5
- **THEN** el sistema emite alerta explícita de riesgo de lesión por sobreentrenamiento y recomienda reducir volumen o intensidad

#### Scenario: ACWR insuficiente (< 4 semanas de datos)
- **WHEN** hay menos de 4 semanas de historial de carga
- **THEN** el sistema retorna ACWR aproximado con advertencia de confianza baja

### Requirement: Recomendación diaria de tipo de día
El sistema SHALL generar al despertar una recomendación de tipo de día (`load`, `active_recovery`, `rest`) basada en la combinación de: estado HRV, Body Battery y ACWR.

#### Scenario: Todos los indicadores verdes
- **WHEN** HRV ≥ baseline, Body Battery ≥ 60 y ACWR < 1.3
- **THEN** recomienda `load` — día de entrenamiento de calidad

#### Scenario: Señales mixtas o Body Battery bajo
- **WHEN** cualquiera de los indicadores está en zona reducida (HRV 85–99%, Body Battery 40–59%, ACWR 1.3–1.5)
- **THEN** recomienda `active_recovery` con entrenamiento de baja intensidad

#### Scenario: Señales de alarma
- **WHEN** HRV suprimido (< 85%) o Body Battery < 40 o ACWR > 1.5
- **THEN** recomienda `rest` con explicación de cuál indicador disparó la alerta
