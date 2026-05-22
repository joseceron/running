# Liebre MVP — Infraestructura GCP

Estado actualizado al 2026-05-21.

## Identificadores del proyecto

| Recurso | Valor |
|---|---|
| **PROJECT_ID** | `liebre-mvp` |
| **PROJECT_NUMBER** | `948756297403` |
| **Billing Account** | `016062-34E2B0-99160B` (`liebre.run`) |
| **Región principal** | `us-east1` |
| **Cuenta GCP propietaria** | `info@elexperto.app` |
| **Dominio público** | `liebre.run` (Squarespace) |

## Recursos creados

### APIs habilitadas
`run`, `sqladmin`, `secretmanager`, `firebase`, `identitytoolkit`, `cloudscheduler`, `pubsub`, `artifactregistry`, `cloudbuild`, `iam`, `iamcredentials`, `cloudresourcemanager` (+ defaults).

### Service Account
- **Email**: `liebre-runtime@liebre-mvp.iam.gserviceaccount.com`
- **Roles**: `secretmanager.secretAccessor`, `cloudsql.client`, `pubsub.publisher`, `pubsub.subscriber`, `logging.logWriter`, `monitoring.metricWriter`, `cloudtrace.agent`
- **Uso**: identidad runtime de Cloud Run (`liebre-api` y `liebre-daily-worker`)

### Artifact Registry
- **Repo**: `liebre-images` (Docker, `us-east1`)
- **URI base**: `us-east1-docker.pkg.dev/liebre-mvp/liebre-images`

### Cloud SQL
- **Instancia**: `liebre-db`
- **Engine**: PostgreSQL 16, edición Enterprise
- **Tier**: `db-f1-micro` (614 MiB RAM, shared core, ~$8-10/mes)
- **Región/zona**: `us-east1`, `zonal` (no HA en MVP)
- **Disco**: SSD 10 GB
- **Backup**: diario a 07:00 UTC
- **IP pública**: `104.196.107.103`
- **Connection name**: `liebre-mvp:us-east1:liebre-db`
- **Database de app**: `liebre`
- **Usuario de aplicación**: `liebre_app` (NO usar `postgres` root desde la app)
- **Connection string (vía Cloud SQL Auth Proxy)**: `postgresql://liebre_app:<password>@127.0.0.1:5432/liebre`
- **Connection string (desde Cloud Run con Auth Proxy lateral)**: `postgresql://liebre_app:<password>@/liebre?host=/cloudsql/liebre-mvp:us-east1:liebre-db`

### Secret Manager
- `postgres_root_password` (versión 1) — credencial root de Postgres (solo para administración)
- `postgres_app_password` (versión 1) — credencial del usuario `liebre_app` (la que usa la API)

### Firebase Auth — providers habilitados
- ✅ **Google** (passwordless, primario)
- ✅ **Teléfono SMS** (passwordless, secundario; cuota gratis 1,000 SMS/día)
- ❌ Email/password — desactivado por decisión UX

### Pub/Sub
- Topic `daily-runs` — fanout del reporte diario por usuario
- Topic `daily-runs-dlq` — dead-letter para mensajes fallidos

### Firebase
- Firebase añadido al proyecto GCP (Auth + App Hosting disponibles)
- Console: https://console.firebase.google.com/project/liebre-mvp/overview

## Pendientes que requieren consola web (no se pueden via CLI)

1. **Activar provider email/password** en Firebase Auth:
   https://console.firebase.google.com/project/liebre-mvp/authentication/providers → "Email/Password" → Enable
2. **Activar provider Google OAuth** en Firebase Auth:
   En la misma página → "Google" → Enable → Project support email → guardar
3. **Configurar dominio autorizado** `liebre.run` para Auth:
   Authentication → Settings → Authorized domains → Add domain → `liebre.run`
4. **Habilitar Firebase App Hosting** cuando lleguemos a deploy del frontend (Semana 3-5):
   https://console.firebase.google.com/project/liebre-mvp/apphosting

## Workflow de migrations (Alembic)

```bash
# Local (Postgres del docker-compose)
export DATABASE_URL="postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre"
alembic upgrade head                                # aplicar todas las pendientes
alembic revision --autogenerate -m "descripcion"    # generar nueva tras editar models
alembic current                                     # revisión actual de la DB

# Contra Cloud SQL (vía Auth Proxy lateral)
# 1. Levantar proxy en otra terminal:
cloud-sql-proxy liebre-mvp:us-east1:liebre-db
# 2. Aplicar:
APP_PASS=$(gcloud secrets versions access latest --secret=postgres_app_password)
DATABASE_URL="postgresql+psycopg2://liebre_app:${APP_PASS}@127.0.0.1:5432/liebre" \
  alembic upgrade head
```

Reglas:
- Las migrations se aplican **antes** de cada deploy de Cloud Run (job separado en CI, no en el entrypoint del contenedor — evita carreras entre instancias).
- Cada PR que toca `memory/models.py` debe incluir su migration en `alembic/versions/`. El test `test_models_match_migrations` falla en CI si no.

## Tests

```bash
docker compose up -d        # levanta Postgres local
pytest                       # 23 tests (19 unit + 4 integration con testcontainers)
pytest --cov                 # con reporte de cobertura
```

## Comandos útiles

```bash
# Estado de Cloud SQL
gcloud sql instances describe liebre-db --project=liebre-mvp

# Listar secrets
gcloud secrets list --project=liebre-mvp

# Ver password de postgres (no compartir)
gcloud secrets versions access latest --secret=postgres_root_password --project=liebre-mvp

# Conectar a Postgres desde tu máquina (requiere Cloud SQL Auth Proxy)
gcloud sql connect liebre-db --user=postgres --project=liebre-mvp

# Listar imágenes del registry
gcloud artifacts docker images list us-east1-docker.pkg.dev/liebre-mvp/liebre-images

# Build y push de imagen Cloud Run (cuando exista Dockerfile)
gcloud builds submit --tag us-east1-docker.pkg.dev/liebre-mvp/liebre-images/liebre-api:latest

# Deploy a Cloud Run
gcloud run deploy liebre-api \
  --image=us-east1-docker.pkg.dev/liebre-mvp/liebre-images/liebre-api:latest \
  --service-account=liebre-runtime@liebre-mvp.iam.gserviceaccount.com \
  --region=us-east1 \
  --add-cloudsql-instances=liebre-mvp:us-east1:liebre-db \
  --set-env-vars="GCP_PROJECT_ID=liebre-mvp"
```

## Convenciones

- **Naming de secrets de usuario Garmin**: `garmin_creds_{firebase_uid}` (JSON `{"email":"...","password":"..."}`)
- **Naming de imágenes Docker**: `liebre-{servicio}:{git-sha-corto}` y tag `latest` para la última
- **Variables de entorno** de Cloud Run: `GCP_PROJECT_ID`, `DATABASE_URL`, `ANTHROPIC_API_KEY` (secret), `SCOPUS_API_KEY` (secret), `WOS_API_KEY` (secret)

## Plan B: Garmin Developer Program

`python-garminconnect` es nuestra ingesta en Fase 1. Aplicar al [Garmin Developer Program](https://developer.garmin.com/gc-developer-program/) en paralelo para migrar a OAuth oficial cuando se reciba aprobación (3-6 semanas de trámite). La capa `data/garmin_client.py` aísla la dependencia: migrar solo cambia el contenido del secret y la lógica de obtención del token.
