## ADDED Requirements

### Requirement: Registro de ingesta calórica diaria
El sistema SHALL aceptar ingesta calórica diaria reportada manualmente por el corredor (kcal totales y gramos de proteína) y persistirla en SQLite con timestamp.

#### Scenario: Registro de ingesta del día
- **WHEN** el corredor reporta haber consumido 2800 kcal y 150g de proteína
- **THEN** el sistema persiste el registro en `nutrition_log` con la fecha del día

#### Scenario: Ingesta no reportada
- **WHEN** el corredor no reporta ingesta de un día
- **THEN** el sistema marca el día como `no_data` y no penaliza el balance — solo advierte si hay 3+ días consecutivos sin datos

### Requirement: Balance calórico vs gasto Garmin
El sistema SHALL calcular el balance calórico diario como: `ingesta_kcal - (BMR + calorias_activas_garmin)`. Un balance < -500 kcal durante 3+ días consecutivos SHALL disparar una alerta de déficit calórico crónico.

#### Scenario: Déficit calórico crónico detectado
- **WHEN** el balance calórico fue negativo (< -500 kcal) por 3 o más días consecutivos
- **THEN** el sistema emite alerta: "Déficit calórico crónico detectado — riesgo de pérdida de masa muscular"

#### Scenario: Balance adecuado
- **WHEN** el balance calórico está entre -200 y +300 kcal
- **THEN** el sistema confirma ingesta adecuada para el nivel de entrenamiento

### Requirement: Alerta de ingesta proteica insuficiente
El sistema SHALL alertar si la ingesta proteica diaria es menor a 1.6g por kg de peso corporal del corredor en días de entrenamiento de alto volumen (> 15 km corridos).

#### Scenario: Proteína insuficiente en día de carga
- **WHEN** el corredor corrió > 15 km y reportó < 1.6g/kg de proteína
- **THEN** el sistema emite alerta específica: "Ingesta proteica insuficiente para preservar masa muscular en días de alto volumen"
