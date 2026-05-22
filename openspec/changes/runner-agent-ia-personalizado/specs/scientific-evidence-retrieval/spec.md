## ADDED Requirements

### Requirement: Búsqueda de papers en Scopus por keyword
El sistema SHALL buscar papers en Scopus API usando queries `TITLE-ABS-KEY(...)` con rate limiting de 1 segundo entre peticiones. El resultado SHALL incluir: título, autores, revista, año, DOI y abstract.

#### Scenario: Búsqueda exitosa con resultados
- **WHEN** se busca "running cadence AND injury prevention" en Scopus
- **THEN** se retorna una lista de hasta 5 papers ordenados por relevancia con todos los campos disponibles

#### Scenario: Rate limit respetado
- **WHEN** se realizan múltiples búsquedas consecutivas
- **THEN** el sistema inserta `time.sleep(1)` entre cada petición a Scopus y `time.sleep(1.2)` entre peticiones al Abstract Retrieval API

### Requirement: Búsqueda de papers en Web of Science
El sistema SHALL buscar en WoS Starter API con rate limiting de ~1 req/seg. El resultado SHALL incluir los mismos campos que Scopus para permitir combinación de resultados.

#### Scenario: Búsqueda WoS exitosa
- **WHEN** se busca "HRV AND training load AND endurance runners" en WoS
- **THEN** se retorna una lista de papers con título, autores, revista, año y abstract

### Requirement: Clasificación de nivel de evidencia
El sistema SHALL clasificar cada paper recuperado en: `strong` (RCT o meta-análisis), `moderate` (estudio cohorte o caso-control) o `weak` (estudio observacional, opinión de experto) basado en el tipo de estudio indicado en el abstract o metadatos.

#### Scenario: Paper identificado como meta-análisis
- **WHEN** el abstract o título contiene "meta-analysis" o "systematic review"
- **THEN** el paper se clasifica como `strong` y se prioriza en las citas del reporte

#### Scenario: Paper observacional
- **WHEN** el abstract indica diseño cross-sectional o retrospectivo sin grupo control
- **THEN** el paper se clasifica como `weak` y se cita con la aclaración del nivel de evidencia

### Requirement: Caché de búsquedas
El sistema SHALL cachear los resultados de búsqueda en SQLite por query + fecha (TTL: 7 días) para evitar consumir quota de APIs en consultas repetidas.

#### Scenario: Query ya cacheada
- **WHEN** se solicita la misma búsqueda dentro del período TTL
- **THEN** se retornan los resultados del caché sin hacer petición a la API externa
