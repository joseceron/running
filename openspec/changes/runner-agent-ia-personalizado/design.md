## Context

Proyecto greenfield. El corredor (José) tiene experiencia personal con lesiones graves por entrenamiento sin guía técnica. El objetivo es un agente de IA que opere sobre datos reales de Garmin y literatura científica para generar recomendaciones individualizadas — no planes genéricos.

Fase 1: prototipo local con `python-garminconnect` (sin aprobación requerida, inmediato).
Fase 2: migrar solo la capa de ingesta a la Garmin Developer API oficial (push-based) sin tocar la lógica del agente.

Restricciones críticas:
- Las credenciales de Garmin dan acceso a datos de salud sensibles → nunca en el repositorio.
- El baseline HRV debe construirse con datos reales del corredor (2–3 semanas), no con valores de literatura.

## Goals / Non-Goals

**Goals:**
- Integrar datos de Garmin (salud + running dynamics) con análisis de fatiga, técnica y nutrición.
- Generar recomendaciones respaldadas por papers de Scopus/WoS con cita específica.
- Persistir perfil del corredor y adaptaciones históricas en SQLite.
- Ejecutar ciclos automatizados: diario (al despertar), post-entrenamiento, semanal (lunes).
- Detectar proactivamente riesgo de lesión (ACWR > 1.5) y degradación de técnica durante la actividad.

**Non-Goals:**
- Diagnóstico médico o reemplazo del médico deportivo.
- Soporte multi-usuario en Fase 1 (el agente es para un corredor específico).
- Interfaz web o app móvil en Fase 1 (CLI y reportes en texto).
- Integración automática de nutrición en Fase 1 (ingesta manual o Cronometer en Fase 2).

## Decisions

### D1: Arquitectura multi-agente con Claude como orquestador
**Decisión**: Usar Anthropic Agent SDK con Claude (`claude-sonnet-4-6`) como orquestador que invoca sub-agentes especializados via tool use.
**Alternativas consideradas**:
- Agente monolítico: más simple, pero mezcla responsabilidades y dificulta el mantenimiento y las pruebas unitarias de cada módulo.
- LangChain/LangGraph: más frameworks, más complejidad operacional sin beneficio claro para el caso de uso actual.
**Rationale**: El SDK de Anthropic permite orquestación nativa con tool use sin dependencias adicionales. Los sub-agentes se pueden desarrollar y probar de forma independiente.

### D2: Garmin vía python-garminconnect en Fase 1
**Decisión**: Usar la librería no oficial `python-garminconnect` para el prototipo.
**Alternativas consideradas**:
- API oficial Garmin Developer Program: requiere semanas de aprobación, diseñada para B2B.
**Rationale**: Permite validar la lógica del agente con datos reales hoy. La capa de ingesta (`garmin_client.py`) está aislada; migrar a la API oficial en Fase 2 no requiere cambios en los sub-agentes.
**Riesgo**: La API no oficial puede romperse si Garmin cambia su backend. Mitigación: encapsular en un client con interfaz estable.

### D3: SQLite para persistencia en Fase 1
**Decisión**: SQLite como base de datos local para perfil del corredor y baseline HRV.
**Alternativas consideradas**:
- PostgreSQL: overkill para un único usuario, requiere servidor.
- Archivos JSON: sin queries, sin integridad relacional.
**Rationale**: SQLite es stdlib de Python, sin configuración, suficiente para un corredor. La capa `db.py` abstraerá las queries; migrar a PostgreSQL en producción es un cambio de una línea en `DATABASE_URL`.

### D4: Baseline HRV personal — no poblacional
**Decisión**: El agente construye el baseline HRV del corredor en las primeras 2–3 semanas de uso. Ninguna recomendación de carga se emite antes de tener 14 días de datos.
**Rationale**: El HRV varía enormemente entre individuos. Usar valores de literatura como referencia produce falsas alarmas o recomendaciones incorrectas. Este principio es no negociable.

### D5: Credenciales en .env local
**Decisión**: Todas las credenciales (Garmin, Scopus, WoS, Anthropic) se leen con `python-dotenv` desde `.env` local. El archivo de referencia está en `/Users/jose.ceron/Documents/emira/.env`.
**Rationale**: Los datos de salud de Garmin son sensibles. `.env` está en `.gitignore` desde el primer commit.

## Risks / Trade-offs

- **python-garminconnect puede romperse** → La interfaz de `garmin_client.py` es estable; si la librería falla, se actualiza solo el client. Monitorear issues del repo en GitHub.
- **Quota de APIs científicas** → Scopus: 1 req/seg. WoS: ~1 req/seg. Implementar `time.sleep()` entre llamadas y caché de resultados en SQLite para queries repetidas.
- **Baseline incompleto** → Si el corredor no sincroniza Garmin diariamente en las primeras 2–3 semanas, el baseline será impreciso. Mostrar advertencia explícita si hay menos de 14 días de HRV disponibles.
- **Privacidad** → Las credenciales de Garmin permiten acceso a datos de salud muy sensibles. Considerar cifrado de la base de datos SQLite en versiones futuras.

## Migration Plan

No aplica en Fase 1 (greenfield). Para la transición Fase 1 → Fase 2:
1. Implementar `GarminOfficialClient` con la misma interfaz que `GarminConnectClient`.
2. Cambiar `GARMIN_CLIENT_CLASS=official` en `.env`.
3. No modificar ningún sub-agente.

## Open Questions

- ¿Se integrará la ingesta de nutrición con Cronometer API o se mantendrá como input manual indefinidamente?
- ¿Cuál será el canal de entrega del reporte diario — terminal, email, WhatsApp?
- ¿Se construirá un sub-agente de riesgo cardiovascular explícito (para el caso de muerte en carrera) o se maneja dentro de `fatigue-load-monitoring`?
