## ADDED Requirements

### Requirement: Perfil base del corredor
El sistema SHALL persistir en SQLite: nombre, edad, peso actual, altura, historial de lesiones (fecha, tipo, severidad, recuperación), metas (evento objetivo, fecha objetivo, tiempo objetivo) y fecha de inicio del sistema.

#### Scenario: Creación de perfil nuevo
- **WHEN** se ejecuta el sistema por primera vez
- **THEN** se solicita al corredor los datos básicos y se persisten en la tabla `runner_profile`

#### Scenario: Actualización de peso
- **WHEN** el corredor reporta un nuevo peso
- **THEN** se guarda el nuevo valor con timestamp en `body_weight_history`; el valor anterior no se elimina

### Requirement: Baseline HRV personal
El sistema SHALL construir y mantener el baseline HRV del corredor calculado como la media móvil de 7 días sobre los últimos 14 días de registros nocturnos. El baseline SHALL marcarse como "no disponible" hasta tener al menos 14 días de datos.

#### Scenario: Baseline en construcción (< 14 días)
- **WHEN** hay menos de 14 registros de HRV nocturno en la base de datos
- **THEN** el sistema retorna `baseline_hrv=None` y emite advertencia: "Baseline en construcción, N/14 días disponibles"

#### Scenario: Baseline disponible
- **WHEN** hay 14 o más registros de HRV
- **THEN** el sistema retorna el baseline como media móvil de 7 días calculada sobre los últimos 14 registros

### Requirement: Historial de adaptaciones
El sistema SHALL registrar para cada semana: plan propuesto vs ejecución real, métricas promedio de la semana (HRV, Body Battery, ACWR) y observaciones del agente sobre qué funcionó y qué no.

#### Scenario: Registro semanal
- **WHEN** el orquestador completa la revisión semanal del lunes
- **THEN** se persiste un registro en `weekly_history` con los datos de la semana anterior

#### Scenario: Consulta de historial
- **WHEN** el plan adaptativo necesita contexto de semanas anteriores
- **THEN** puede consultar las últimas N semanas con sus métricas y observaciones
