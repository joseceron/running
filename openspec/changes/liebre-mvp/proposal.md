## Why

El sistema personal `runner-agent` (change `runner-agent-ia-personalizado`) está funcional y ha entregado resultados validados con datos reales de José: en una semana, su distribución Z4 bajó de 33% a 0,6%; su FC en reposo bajó de 56 a 50 lpm; el HRV responde correctamente al descanso. El núcleo científico (5 sub-agentes + clientes Scopus/WoS) es reutilizable. Sin embargo, está acoplado a un único usuario: la base de datos no tiene `user_id`, las credenciales Garmin viven en `.env` global, el perfil del corredor es una fila única (`LIMIT 1`).

El mercado de apps para corredores está dominado por sistemas que usan rangos poblacionales genéricos. Una persona murió en una carrera el año pasado por desconocer su condición real; José sufrió un desgarro del 49% del sóleo por mala técnica. El diferenciador comercial de **Liebre** (la liebre es el corredor que marca el paso en carreras) es: **análisis con baseline propio del usuario + recomendaciones respaldadas por papers citados**, frente a apps genéricas. Misión: democratizar el correr seguro con IA + ciencia.

Este change convierte el motor personal en un producto SaaS multiusuario en 5 semanas, con landing pública + onboarding + dashboard, sin perder la lógica científica ya validada.

## What Changes

- **Refactor multi-tenant** del backend Python: `user_id` (= Firebase Auth UID) propagado a toda la persistencia y a los agentes; cero variables globales con perfil del corredor.
- **Migración SQLite → Postgres Cloud SQL** preservando schemas; script de import que coloca al José actual como primer usuario.
- **Capa API REST nueva** (FastAPI) sobre el núcleo Python, desplegada en Cloud Run con un Dockerfile único. Sin Firebase Functions: triggers de Auth se emulan desde el frontend llamando endpoints.
- **Conexión Garmin per-user** con credenciales cifradas en Google Secret Manager (un secret por UID). Tokens garth en `/tmp/garmin_tokens_{uid}` por instancia.
- **Frontend nuevo** Next.js 16 + Tailwind 4 sobre Firebase App Hosting (SSR), clonando el design system de `doctorandos/landing` y recoloreándolo en deportivo.
- **Firebase Auth** (Google + Teléfono SMS, passwordless por decisión UX) como sistema de identidad; UID es la clave maestra en toda la plataforma. El número de teléfono queda alineado con el identificador de WhatsApp para Fase 2.
- **Onboarding multi-paso** (perfil → conexión Garmin → backfill) con `react-hook-form + zod`.
- **Dashboard básico**: HRV vs baseline, ACWR, Body Battery + recomendación del día, VO2max, daily report markdown, plan semanal, citas científicas.
- **Cloud Scheduler + Pub/Sub** para correr el reporte diario por usuario (fan-out con concurrencia limitada).

## Capabilities

### New Capabilities

- `multi-tenant-persistence`: Esquema Postgres con `user_id` en todas las tablas relacionadas; índices `(user_id, date)`; `science_cache` permanece global compartido.
- `garmin-per-user-credentials`: Almacenamiento cifrado de credenciales Garmin en Secret Manager con políticas de acceso, rotación y borrado por usuario.
- `firebase-auth-identity`: Integración con Firebase Auth (Google + Teléfono, sin email/password) como proveedor de identidad; UID como `user_id` canónico.
- `rest-api-fastapi`: API REST con FastAPI sobre Cloud Run: onboarding, conexión Garmin, daily report, weekly plan, dashboard agregado, webhook WhatsApp (Fase 2).
- `nextjs-saas-frontend`: Landing pública + área privada SSR sobre Firebase App Hosting; design system recoloreado deportivo.
- `onboarding-flow-multistep`: Flujo de 3 pasos (perfil físico/meta → credenciales Garmin con disclaimer → pantalla de sync con polling).
- `runner-dashboard`: Vista privada con cards/gráficos sobre HRV, ACWR, Body Battery, VO2max, daily report, plan semanal y evidencia científica.
- `scheduled-daily-fanout`: Cloud Scheduler + Pub/Sub que dispara el reporte diario por usuario a las 6 AM (Bogotá), con concurrencia limitada.

### Modified Capabilities

- `garmin-data-ingestion` → ahora acepta `user_id` y resuelve credenciales desde Secret Manager.
- `runner-memory-profile` → schema migrado a Postgres; queries con `user_id`; sin más `LIMIT 1`.
- `fatigue-load-monitoring`, `running-technique-analysis`, `adaptive-training-plan`, `nutrition-monitoring`, `orchestrator-agent` → todos aceptan `user_id` como primer argumento.
- `scientific-evidence-retrieval` → caché compartido global, sin cambios funcionales.

## Impact

- **Dependencias externas nuevas**: `fastapi`, `uvicorn`, `psycopg2-binary` (o `SQLAlchemy`), `google-cloud-secret-manager`, `firebase-admin`, `google-cloud-pubsub`, `google-cloud-run` (deploy), `pydantic`. Frontend: Next.js 16, React 19, Tailwind 4, `react-hook-form`, `zod`, `recharts`, `react-markdown`, `firebase` (web SDK).
- **APIs externas**: añadidas Cloud Run, Cloud SQL, Secret Manager, Firebase Auth, Firebase App Hosting, Cloud Scheduler, Pub/Sub. Anthropic API con prompt caching habilitado.
- **Credenciales sensibles**: credenciales Garmin de cada usuario cifradas en Secret Manager (AES-256-GCM gestionado por Google); NUNCA en Postgres ni en logs. Audit logs habilitados.
- **Cumplimiento legal**: T&C en español; consentimiento explícito para almacenar credenciales; endpoint `DELETE /v1/users/me` que purga Postgres + Secret Manager; Habeas Data (Colombia) + base para GDPR.
- **Compatibilidad con sistema actual**: `runner-agent` sigue corriendo con `python main.py daily` durante la transición. El primer usuario migrado es José.
- **Dominio**: `liebre.run` ya comprado (Squarespace, 2026-05-21).
- **Infraestructura GCP**: proyecto nuevo `liebre-mvp` con billing account separado (lo crea José en consola; el resto vía gcloud CLI).
