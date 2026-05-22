## 1. Infraestructura GCP / Firebase (Semana 1)

- [ ] 1.1 José crea proyecto GCP nuevo `liebre-mvp` y billing account separado en consola
- [ ] 1.2 `gcloud config set project liebre-mvp` y habilitar APIs: `run.googleapis.com`, `sqladmin.googleapis.com`, `secretmanager.googleapis.com`, `firebase.googleapis.com`, `cloudscheduler.googleapis.com`, `pubsub.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`
- [ ] 1.3 Provisionar Cloud SQL Postgres `db-f1-micro` en `us-east1`, instancia `liebre-db`, contraseña aleatoria guardada en Secret Manager (`postgres_root_password`)
- [ ] 1.4 Habilitar Firebase en el proyecto, configurar Firebase Auth con providers email/password + Google
- [ ] 1.5 Configurar Artifact Registry repo `liebre-images` en `us-east1`
- [ ] 1.6 Crear service account `liebre-runtime@liebre-mvp.iam.gserviceaccount.com` con roles: `secretmanager.secretAccessor`, `cloudsql.client`, `pubsub.publisher`, `pubsub.subscriber`
- [ ] 1.7 Documentar todos los IDs y endpoints en `runner-agent/infra/README.md`

## 2. Refactor de persistencia (Semana 1)

- [ ] 2.1 Crear `runner-agent/memory/db.py` v2 con SQLAlchemy + `psycopg2-binary` apuntando a Postgres (variable `DATABASE_URL`)
- [ ] 2.2 Migrar schema: añadir `user_id TEXT NOT NULL` a `runner_profile`, `hrv_log`, `weekly_history`, `nutrition_log`, `body_weight_history`; índice compuesto `(user_id, date)`; PK con `user_id`
- [ ] 2.3 `science_cache` permanece global (sin `user_id`)
- [ ] 2.4 Crear `runner-agent/memory/repositories/` con un módulo por tabla, todos con `user_id` como primer arg
- [ ] 2.5 Crear `runner-agent/scripts/migrate_sqlite_to_postgres.py`: lee SQLite local, inserta filas en Postgres con `user_id = JOSE_UID_PLACEHOLDER`
- [ ] 2.6 Test de paridad: `pytest runner-agent/tests/test_migration.py` valida que para todas las queries del orchestrator, Postgres y SQLite producen el mismo resultado para el user de José
- [ ] 2.7 Docker compose local con Postgres 16 para desarrollo

## 3. Refactor garmin_client per-user (Semana 2)

- [ ] 3.1 `data/garmin_client.py`: `GarminConnectClient(user_id: str)` resuelve credenciales con `google.cloud.secretmanager.SecretManagerServiceClient` desde `projects/liebre-mvp/secrets/garmin_creds_{uid}/versions/latest`
- [ ] 3.2 Token store por usuario en `/tmp/garmin_tokens_{uid}` (volátil; se re-loguea en cold starts si no existe)
- [ ] 3.3 Logger con `logging.Filter` que enmascara `password|GARMIN_*` y nunca imprime payload del secret
- [ ] 3.4 Función `connect_garmin(user_id, email, password)`: valida login, crea secret en Secret Manager, guarda payload JSON
- [ ] 3.5 Función `disconnect_garmin(user_id)`: `disable + destroy` todas las versiones del secret
- [ ] 3.6 Test unitario con mock de `garminconnect` y `secretmanager` que valida no-leak de credenciales en logs

## 4. Propagación de user_id en agentes (Semana 2)

- [ ] 4.1 `agents/fatigue_agent.py`: `analyze_day(user_id, date, body_battery, recent_activities, max_hr)`
- [ ] 4.2 `agents/technique_agent.py`: `analyze_session(user_id, activity)`
- [ ] 4.3 `agents/plan_agent.py`: `generate_weekly_plan(user_id, runner_data)`
- [ ] 4.4 `agents/science_agent.py`: sin cambios (cache global)
- [ ] 4.5 `agents/nutrition_agent.py`: `check_chronic_deficit(user_id)`, `check_protein_alert(user_id, date, km_run)`
- [ ] 4.6 `agents/orchestrator.py`: `run_daily_report(user_id, target_date)`, `run_post_run_analysis(user_id)`, `run_weekly_review(user_id)`; cliente Anthropic compartido con prompt caching del system prompt
- [ ] 4.7 Test de aislamiento: dos `user_id` distintos producen reportes independientes; ningún query falla por leak

## 5. API REST FastAPI sobre Cloud Run (Semana 2)

- [ ] 5.1 `runner-agent/api/main.py` con FastAPI + CORS configurado para `https://liebre.run`
- [ ] 5.2 Middleware `api/middleware/auth.py`: verifica `Authorization: Bearer <firebase_id_token>` con `firebase_admin.auth.verify_id_token` e inyecta `request.state.user_id`
- [ ] 5.3 Router `users`: `POST /v1/users/me/init` (llamado tras signup), `POST /v1/users/me/onboarding` (perfil físico + meta), `DELETE /v1/users/me` (cascade Postgres + Secret Manager)
- [ ] 5.4 Router `garmin`: `POST /v1/users/me/garmin/connect` (email+password en body → valida → guarda secret → dispara backfill), `DELETE /v1/users/me/garmin` (revoke)
- [ ] 5.5 Router `reports`: `GET /v1/users/me/daily-report?date=`, `GET /v1/users/me/weekly-plan`, `GET /v1/users/me/dashboard` (payload agregado)
- [ ] 5.6 Endpoint async para backfill: `POST /v1/users/me/garmin/backfill` que enqueue mensaje Pub/Sub y devuelve `202 Accepted`
- [ ] 5.7 Endpoint placeholder `POST /webhooks/whatsapp` (Fase 2; HMAC verify ya cableado)
- [ ] 5.8 `runner-agent/infra/Dockerfile` multi-stage Python 3.11-slim
- [ ] 5.9 `runner-agent/infra/cloudbuild.yaml` que construye e imagen y la sube a Artifact Registry
- [ ] 5.10 `gcloud run deploy liebre-api` con la imagen, vinculado a Cloud SQL via Cloud SQL Auth Proxy, service account `liebre-runtime`, env `DATABASE_URL`, `GCP_PROJECT_ID`

## 6. Frontend Next.js (Semana 3)

- [ ] 6.1 `cp -r /Users/jose.ceron/Documents/dev/doctorandos/landing/* /Users/jose.ceron/Documents/dev/running/web/` (sin sobrescribir si existe; revisar manualmente)
- [ ] 6.2 Quitar `output:"export"` en `web/next.config.ts`; añadir `experimental: { serverActions: { ... } }` si se usan
- [ ] 6.3 Recoloreo deportivo: actualizar `web/src/app/globals.css` con paleta nueva (blanco hueso, tinta, turquesa, rojo señal — paleta validada con José antes de continuar)
- [ ] 6.4 Reescribir `Hero`, `ComoFunciona`, `Diferenciales`, `FAQ`, `CTAFinal`, `Footer` con copy de Liebre (en español; misión democratizar correr seguro)
- [ ] 6.5 Borrar componentes que no aplican (`Servicios`, `CasosExito`, `Cotizador`)
- [ ] 6.6 Crear nuevas secciones marketing: `ComoFunciona` (3 pasos), `Ciencia` (badges Scopus/WoS), `Diferencial` (vs apps genéricas)
- [ ] 6.7 `web/src/lib/firebase.ts` con SDK web; init en cliente y server
- [ ] 6.8 `web/src/lib/api.ts`: cliente fetch que agrega `Authorization: Bearer <id_token>`
- [ ] 6.9 Páginas auth: `/login`, `/signup` con Firebase Auth UI (email/password + Google)
- [ ] 6.10 Layout `web/src/app/(app)/layout.tsx` con guard SSR que redirige a `/login` si no hay sesión

## 7. Onboarding multi-paso (Semana 3)

- [ ] 7.1 `web/src/app/(app)/onboarding/perfil/page.tsx`: form `react-hook-form + zod` (edad, sexo, peso, altura, FCmax opcional, meta `{evento, fecha, tiempo_objetivo}`, lesiones, días/semana)
- [ ] 7.2 `web/src/app/(app)/onboarding/garmin/page.tsx`: form email+password Garmin con disclaimer explícito en es-CO, link a política de privacidad
- [ ] 7.3 `web/src/app/(app)/onboarding/sync/page.tsx`: polling cada 3s a `/v1/users/me/garmin/backfill/status`; UI con skeleton y progreso
- [ ] 7.4 Redirect a `/dashboard` cuando `backfill_status == "complete"`

## 8. Dashboard (Semana 4)

- [ ] 8.1 `web/src/app/(app)/dashboard/page.tsx` SSR que fetch `/v1/users/me/dashboard` con `id_token`
- [ ] 8.2 Componente `HRVCard`: valor actual, delta vs baseline 30d, sparkline 14d, semáforo
- [ ] 8.3 Componente `ReadinessCard`: Body Battery + recomendación día (texto del `fatigue_agent`)
- [ ] 8.4 Componente `LoadChart` con `recharts`: barras semanales km + línea ACWR con zona segura 0.8-1.3 sombreada
- [ ] 8.5 Componente `VO2MaxCard`: valor actual + curva proyección hacia meta
- [ ] 8.6 Componente `DailyReportPanel`: markdown del orchestrator renderizado con `react-markdown`
- [ ] 8.7 Componente `WeeklyPlanTable`: 7 filas (lunes-domingo) con tipo de entrenamiento
- [ ] 8.8 Componente `ScienceEvidence`: lista colapsable de papers (autor, año, journal, DOI)
- [ ] 8.9 Estados loading/error/empty para cada card
- [ ] 8.10 Smoke test con cuenta real de José en staging

## 9. Cloud Scheduler + Pub/Sub (Semana 4)

- [ ] 9.1 Crear topic Pub/Sub `daily-runs`
- [ ] 9.2 Cloud Run worker job `liebre-daily-worker` (segundo servicio Cloud Run o un endpoint dedicado) que consume mensajes y ejecuta `run_daily_report(user_id)`
- [ ] 9.3 Subscriber con concurrencia limitada (max 10 mensajes simultáneos)
- [ ] 9.4 Cloud Scheduler job `liebre-daily-fanout` a las 6 AM (Bogotá, `0 6 * * *` con TZ `America/Bogota`): hace fan-out publicando un mensaje por `user_id` activo
- [ ] 9.5 Dead-letter topic + alerta a email del admin

## 10. Deploy y lanzamiento (Semana 5)

- [ ] 10.1 Comprar y configurar custom domain `liebre.run` en Firebase App Hosting (DNS apuntando a Firebase)
- [ ] 10.2 Configurar mapping `api.liebre.run` → Cloud Run service
- [ ] 10.3 Habilitar SSL automático (Firebase + Cloud Run con custom domain)
- [ ] 10.4 Reusar `Analytics.tsx` de doctorandos con nuevos IDs: Google Analytics 4 + Meta Pixel
- [ ] 10.5 Configurar Sentry (proyectos web + backend) para error tracking
- [ ] 10.6 Redactar y publicar T&C, política de privacidad y aviso de Habeas Data (CO) en español
- [ ] 10.7 Smoke E2E con 2 usuarios distintos (José + 1 tester): aislamiento de datos confirmado
- [ ] 10.8 Brief para Lida (nutricionista en Medellín) con onboarding link de prueba
- [ ] 10.9 Configurar Google Ads (presupuesto inicial limitado, ~$50/día) con segmento "corredores LATAM 25-45"
- [ ] 10.10 Setup de alerta de budget GCP en $50

## 11. Validación final

- [ ] 11.1 Verificar que ningún log de Cloud Run contiene credenciales Garmin (test automático con `grep` en logs después de un onboarding)
- [ ] 11.2 Verificar que `DELETE /v1/users/me` deja Postgres y Secret Manager limpios para ese UID
- [ ] 11.3 Validar aislamiento: el daily report de user A nunca contiene datos de user B (test integración)
- [ ] 11.4 Validar que el sistema CLI personal de José sigue corriendo en paralelo (no se rompe nada)
- [ ] 11.5 Documentar en `README.md` del root: arquitectura, deploy, troubleshooting, comandos útiles
- [ ] 11.6 Aplicar a Garmin Developer Program en paralelo (plan B documentado en `runner-agent/infra/garmin-oauth-roadmap.md`)
