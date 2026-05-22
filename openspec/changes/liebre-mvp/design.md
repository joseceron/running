## Context

El change anterior (`runner-agent-ia-personalizado`) construyó un sistema personal funcional con 5 sub-agentes coordinados por Claude. Los datos reales lo validan: José pasó de correr 80% en Z4-Z5 a una distribución 80/20 saludable en una semana; su HRV responde correctamente al descanso; el sistema detecta degradación de técnica.

El paso a SaaS no requiere reescribir la lógica científica — solo aislarla, parametrizarla con `user_id` y exponerla detrás de una API con auth. La complejidad nueva está en: (1) multi-tenancy seguro de credenciales Garmin, (2) onboarding sin fricción, (3) un dashboard que comunique valor en los primeros 60 segundos.

Restricciones críticas:
- Las credenciales Garmin son datos extremadamente sensibles; el almacenamiento en claro está descartado.
- El producto se lanza primero en LATAM; la región GCP debe estar cerca (`us-east1` cumple).
- El usuario quiere mínima fragmentación operativa: un Docker, un deploy, una base de datos.
- Garmin no ofrece OAuth público para individuos; usar `python-garminconnect` es aceptable como Fase 1 con plan B documentado.

## Goals / Non-Goals

**Goals:**
- Refactorizar `runner-agent` a multi-tenant sin romper el flujo single-user actual de José.
- Exponer el núcleo Python como API REST autenticada con Firebase ID tokens.
- Frontend Next.js con landing pública, signup, onboarding 3-pasos y dashboard básico.
- Almacenar credenciales Garmin en Secret Manager con política de borrado total por usuario.
- Deploy automatizable con `gcloud run deploy` y `firebase deploy --only hosting`.
- Documentar plan B para migrar a Garmin Developer Program cuando se reciba aprobación.

**Non-Goals:**
- WhatsApp y agente cron diario completos (se planean para Fase 2 — webhook en API queda como esqueleto).
- Soporte de Coros u otras plataformas no-Garmin en este MVP.
- App móvil nativa.
- Sistema de pagos / Stripe (freemium se valida primero con waitlist de premium).
- Internacionalización; solo español en MVP.
- Integración automática de nutrición (queda manual o se pospone).

## Decisions

### D1: Backend único en Cloud Run, sin Firebase Functions
**Decisión**: Un solo Docker con FastAPI desplegado en Cloud Run. Todos los handlers (incluyendo lo que normalmente iría en `onUserCreate` triggers) viven como endpoints REST llamados desde el frontend.
**Alternativas consideradas**:
- Firebase Functions Gen2 (Python): timeout de 9 min insuficiente para orchestrator + Claude; bundles pesados con `garminconnect` + scientific libs causan cold starts lentos; obliga a fragmentar la lógica entre dos runtimes.
- Híbrido Cloud Run + Functions: más piezas que mantener, más latencia entre saltos.
**Rationale**: Cloud Run escala a 0 (costo ~0 idle), timeout 60 min, sin límite de bundle, mismo runtime que el código de José ya usa. El usuario aceptó: "todo en docker, no vamos a tener mucha recurrencia al inicio".

### D2: Postgres Cloud SQL como única DB (no Firestore híbrido)
**Decisión**: Toda la persistencia en Postgres Cloud SQL `db-f1-micro` en `us-east1`. Schemas migrados 1:1 desde SQLite con `user_id` añadido.
**Alternativas consideradas**:
- Solo Firestore: queries de baseline HRV rolling 30d, ACWR (carga aguda 7d / crónica 28d) y agregaciones científicas requieren precomputar documentos; complica el código del orchestrator y los agentes ya escritos.
- Híbrido Firestore + Postgres: dos modelos mentales, sincronización, doble fuente de verdad.
**Rationale**: El usuario decidió Postgres. La migración SQLite→Postgres es trivial (cambiar driver, añadir `user_id`). Los agentes Python siguen usando SQL directo. UI consume API REST con polling; no necesitamos realtime listeners de Firestore en MVP.

### D3: Garmin per-user vía python-garminconnect + Secret Manager
**Decisión**: Cada usuario ingresa email+password de Garmin en el onboarding. El backend valida login, guarda `{email, password}` JSON como un secret en Secret Manager (`garmin_creds_{uid}`) y descifra on-the-fly en cada job. Tokens garth volátiles en `/tmp/garmin_tokens_{uid}`.
**Alternativas consideradas**:
- Garmin Developer Program (OAuth): requiere aplicar y aprobación 3-6 semanas; descartado para MVP, se aplica en paralelo como plan B.
- Cifrado AES con clave maestra en .env: clave única => si se filtra, comprometo a todos los usuarios. Sin auditoría nativa.
- Firestore + Cloud KMS: posible pero añade una pieza más; Secret Manager es el primitivo correcto para credenciales.
**Rationale**: Secret Manager es el servicio diseñado para esto: AES-256-GCM, versionado, audit logs, IAM granular, borrado seguro. El plan B (OAuth) solo cambia el contenido del secret, no la arquitectura.
**Riesgo aceptado**: Garmin podría bloquear logins por volumen desde la IP de Cloud Run. Mitigación: NAT estática, tokens persistentes para evitar re-login frecuente, backoff exponencial, plan B OAuth.

### D4: Firebase Auth como identidad única, passwordless first
**Decisión**: Firebase Auth con providers **Google + Teléfono SMS** únicamente (NO email/password). UID de Firebase Auth es la `user_id` canónica en Postgres y en Secret Manager.
**Alternativas consideradas**:
- Email/password como provider primario: descartado porque los usuarios olvidan credenciales y abandonan (feedback explícito de José basado en experiencia previa con productos).
- Auth.js (NextAuth) self-hosted: más flexible pero requiere mantener tablas de sesión, JWT, providers manualmente.
- Clerk: excelente UX pero costo escalado en SaaS B2C es relevante; lock-in.
**Rationale**: Firebase Auth tier gratuito hasta 50k MAU; ya está en el stack (App Hosting); UID estable; SDK web y Python (`firebase-admin`) maduros; el verify del ID token en el middleware de FastAPI es 5 líneas. **El teléfono del auth queda alineado con el identificador de WhatsApp para Fase 2**, lo que evita reconciliación de identidad entre canales. Costo SMS: ~USD $0.05-0.10 por mensaje fuera del tier gratis de Firebase (~10 SMS/proyecto/día); aceptable para MVP.

### D5: Next.js 16 SSR sobre Firebase App Hosting
**Decisión**: Frontend Next.js 16 con App Router, sin `output:"export"`. Desplegado en Firebase App Hosting (SSR nativo).
**Alternativas consideradas**:
- Vercel: excelente DX pero introduce un proveedor más; el usuario ya tiene Firebase pago para `academ-ia-mvp`.
- Next.js static export + auth client-side: limita SEO de páginas privadas (OK aquí, son privadas) pero rompe SSR de dashboard y dificulta middleware de auth en edge.
**Rationale**: App Hosting está hecho para Next.js SSR; mismo proyecto GCP/Firebase que el resto; deploy con `firebase deploy --only hosting`.

### D6: Sin OpenAPI generado, sino tipado manual del cliente
**Decisión**: FastAPI genera `/openapi.json`; en el frontend definimos types manualmente en `web/src/lib/api.ts` para los <10 endpoints del MVP. Si crece, agregamos `openapi-typescript`.
**Rationale**: 10 endpoints no justifican el setup de codegen. Velocidad > pureza.

## Risks / Trade-offs

- **Bloqueo de IP Garmin**: NAT estática + rate limit cliente + cache de tokens garth por usuario + plan B OAuth aplicado en paralelo. Mitigación de impacto: si pasa, los usuarios verán un "estamos resolviendo, vuelve en una hora"; ningún dato se pierde.
- **Costo Claude por usuario**: prompt caching del system prompt (>1024 tokens estáticos = 90% descuento en hits), reportes 1×/día, freemium con cuota explícita (a definir). Alerta de budget en GCP Billing.
- **Datos de salud sensibles + Habeas Data CO + GDPR**: T&C en español, DPA explícito, endpoint DELETE que cascadea Postgres + Secret Manager, audit logs habilitados, región us-east1 cerca de LATAM.
- **`python-garminconnect` activamente mantenido pero no oficial**: pin de versión exacta; mirror del repo en GitHub privado como safety net; capa `garmin_client.py` aísla la dependencia.
- **`output:"export"` en `doctorandos` incompatible**: cambio puntual en `next.config.ts` al clonar; suficiente.
- **Latencia del orchestrator**: Claude puede tardar 20-40s; el dashboard inicial carga datos de Postgres mientras tanto y el daily report se renderiza de forma async (skeleton).
- **Concurrencia del fanout diario**: 6 AM Bogotá significa muchos jobs en pocos minutos; Pub/Sub con concurrencia limitada (10-20 en paralelo) y backoff exponencial. Para MVP con <100 usuarios no es problema.

## Migration Plan

**Paso 0 — Sistema actual sigue corriendo**: `runner-agent` con SQLite local mantiene a José en producción durante toda la migración. No se rompe nada hasta el switchover final.

**Paso 1 — Esquema Postgres con `user_id`**:
1. Provisionar Cloud SQL `db-f1-micro` en `us-east1`.
2. Crear schema con `user_id TEXT NOT NULL` añadido a las 5 tablas relacionadas.
3. Script `scripts/migrate_sqlite_to_postgres.py`: lee SQLite local de José, inserta filas con `user_id = JOSE_FIREBASE_UID` (creado a mano para la migración).
4. Tests de paridad: el `daily_morning_check` corrido contra Postgres produce el mismo output que contra SQLite.

**Paso 2 — Refactor agentes con `user_id`**:
1. `data/garmin_client.py`, `agents/*.py`, `agents/orchestrator.py`: añadir `user_id` como primer argumento.
2. Tests unitarios que validen aislamiento (un user no ve datos de otro).

**Paso 3 — API REST FastAPI**:
1. `runner-agent/api/main.py` con middleware Firebase Auth.
2. Endpoints `onboarding`, `garmin/connect`, `dashboard`, `daily-report`, `weekly-plan`.
3. Dockerfile + cloudbuild.yaml.
4. Deploy a Cloud Run.

**Paso 4 — Frontend**:
1. `cp -r doctorandos/landing web/`.
2. Quitar `output:"export"`, recolorear, reescribir copy.
3. Firebase Auth UI + onboarding 3 pasos + dashboard.

**Paso 5 — Cutover**:
1. José se registra en `liebre.run` con su email.
2. Su `user_id` Firebase reemplaza el placeholder de la migración (script de reasignación).
3. Conecta su Garmin desde el flujo de onboarding (no más `.env` global).
4. Sistema CLI personal se mantiene 30 días como rollback antes de desactivarse.

## Open Questions

- **Pricing**: ¿USD/mes premium? Pendiente análisis competencia (One Running, Stryd, etc.).
- **Cuotas freemium**: ¿3 daily reports/sem? ¿bloquear plan semanal? ¿citas científicas detrás del paywall?
- **Backfill histórico**: ¿descargar últimos 90 días al conectar Garmin, o solo 30? Trade-off entre tiempo de espera del onboarding y completitud del baseline.
- **Soporte Coros / Polar / Apple Health**: roadmap post-MVP; ¿prioridad después de Garmin?
- **Diseño visual definitivo**: paleta tentativa (#F8F7F2, #0E1116, #00B8A9, #FF4D5E) requiere mockup antes de implementación; ¿José genera referencias o se le delega al Claude design skill?
- **Política de retención de datos**: ¿cuánto tiempo se guardan HRV/actividades de un usuario que se da de baja? Default sugerido: borrado total inmediato en DELETE; el secret de Garmin se destruye irreversiblemente.
