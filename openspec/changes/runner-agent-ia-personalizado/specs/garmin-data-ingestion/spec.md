## ADDED Requirements

### Requirement: Autenticación con Garmin Connect
El sistema SHALL autenticarse con Garmin Connect usando email y password leídos de variables de entorno (`GARMIN_EMAIL`, `GARMIN_PASSWORD`) via `python-dotenv`. Las credenciales NUNCA deben aparecer en el código fuente.

#### Scenario: Autenticación exitosa
- **WHEN** el cliente se inicializa con credenciales válidas en `.env`
- **THEN** la sesión queda activa y lista para hacer peticiones

#### Scenario: Credenciales inválidas
- **WHEN** el email o password son incorrectos
- **THEN** el sistema lanza una excepción descriptiva y no continúa la ejecución

### Requirement: Extracción de métricas de salud diarias
El sistema SHALL extraer para una fecha dada: HRV nocturno, Body Battery, frecuencia cardíaca en reposo, SpO₂, score de sueño (con fases REM/profundo/ligero), nivel de estrés diario y VO₂Max estimado.

#### Scenario: Datos disponibles para la fecha
- **WHEN** se solicitan métricas de salud para una fecha en que el reloj sincronizó datos
- **THEN** se retorna un dict con todos los campos; los campos no disponibles retornan `None`

#### Scenario: Datos no disponibles
- **WHEN** se solicitan métricas para una fecha sin sincronización
- **THEN** se retorna un dict con todos los campos en `None` (no se lanza excepción)

### Requirement: Extracción de Running Dynamics por actividad
El sistema SHALL extraer para la última actividad de carrera: cadencia promedio y por km, oscilación vertical, Vertical Ratio, Ground Contact Time (GCT), balance GCT izq/der, longitud de zancada, splits por km, tiempo en zonas de FC (Z1–Z5) y distancia total.

#### Scenario: Última actividad es de tipo carrera
- **WHEN** se solicitan running dynamics de la última actividad
- **THEN** se retornan todas las métricas de biomecánica disponibles para esa sesión

#### Scenario: Última actividad no es de tipo carrera
- **WHEN** la actividad más reciente es ciclismo, natación u otro tipo
- **THEN** se busca la última actividad específicamente de tipo running y se retornan sus métricas

### Requirement: Interfaz estable para migración futura
El cliente Garmin SHALL exponer una interfaz (`get_daily_health`, `get_last_run_dynamics`, `get_hrv_history`) que no cambie al migrar de `python-garminconnect` a la API oficial en Fase 2.

#### Scenario: Cambio de backend
- **WHEN** se instancia `GarminOfficialClient` en lugar de `GarminConnectClient`
- **THEN** los sub-agentes reciben los mismos tipos de datos sin modificación
