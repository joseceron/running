## Why

La mayoría de los corredores — especialmente los que se inician — entrenan sin guía técnica individualizada, lo que genera lesiones por sobrecarga, mala técnica y desconocimiento de sus límites fisiológicos reales. Los planes genéricos ignoran la respuesta individual del cuerpo; el resultado son lesiones graves (como un desgarro del 49% del sóleo por mala técnica) y, en casos extremos, eventos cardiovasculares en carrera. Existe la tecnología (Garmin) y la evidencia científica (Scopus, WoS) para prevenir esto — falta el agente que las una.

## What Changes

- **Nuevo sistema completo**: no existe código previo; se construye desde cero.
- Integración con Garmin para extraer métricas de salud (HRV, Body Battery, VO₂Max, sueño) y técnica de carrera (cadencia, GCT, oscilación vertical, balance izq/der) en tiempo real.
- Motor de análisis de fatiga y carga que opera sobre el baseline **personal** del corredor — no sobre promedios poblacionales.
- Generación de planes de entrenamiento semanales adaptativos basados en la respuesta real del corredor la semana anterior.
- Sub-agente de evidencia científica que respalda cada recomendación con papers de Scopus o Web of Science, citando autor, revista, año y hallazgo clave.
- Perfil persistente del corredor (SQLite) con historial de lesiones, metas, baseline HRV y adaptaciones pasadas.
- Detección proactiva de riesgo de lesión mediante Acute:Chronic Workload Ratio (ACWR > 1.5 = alerta).
- Monitor de nutrición que cruza gasto calórico (Garmin) con ingesta para prevenir déficit calórico crónico y pérdida de masa muscular.

## Capabilities

### New Capabilities

- `garmin-data-ingestion`: Conexión a Garmin via python-garminconnect; extrae datos de salud y running dynamics por sesión y por día.
- `runner-memory-profile`: Perfil persistente del corredor en SQLite: datos personales, historial de lesiones, metas, baseline HRV, historial de adaptaciones.
- `fatigue-load-monitoring`: Análisis de HRV vs baseline personal, cálculo de ACWR, recomendación diaria (carga / recuperación / off), alerta de sobreentrenamiento.
- `running-technique-analysis`: Análisis de cadencia, oscilación vertical, Vertical Ratio, GCT y balance izq/der; detecta degradación de forma durante la actividad.
- `adaptive-training-plan`: Generación de plan semanal ajustado a datos reales; ritmos en zonas de FC personalizadas según estado del día (no ritmos genéricos).
- `scientific-evidence-retrieval`: Búsqueda en Scopus y Web of Science por keyword; retorna abstract + cita formateada; diferencia RCTs/meta-análisis de estudios observacionales.
- `nutrition-monitoring`: Cruza gasto calórico Garmin con ingesta reportada; detecta déficit calórico crónico y riesgo de pérdida de masa muscular.
- `orchestrator-agent`: Agente principal Claude que coordina todos los sub-agentes y genera los reportes diarios y semanales.

### Modified Capabilities

*(ninguna — proyecto nuevo)*

## Impact

- **Dependencias externas nuevas**: `garminconnect`, `anthropic`, `requests`, `python-dotenv`, `apscheduler`, `sqlite3` (stdlib).
- **APIs externas**: Garmin Connect (no oficial, Fase 1), Scopus API (Elsevier), Web of Science API (Clarivate).
- **Credenciales**: almacenadas en `.env` local (nunca en el repo); cargadas con `python-dotenv`. Archivo de referencia en `/Users/jose.ceron/Documents/emira/.env`.
- **Datos de salud sensibles**: las credenciales Garmin dan acceso a datos fisiológicos completos; diseño con privacidad desde el inicio.
- **Sin impacto en sistemas existentes**: proyecto greenfield, sin integraciones con código previo.
