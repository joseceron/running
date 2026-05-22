# Liebre

> La liebre es quien marca el paso en una carrera profesional.

Liebre es un producto SaaS para corredores que combina **datos biomecánicos reales de Garmin** (HRV, running dynamics, Body Battery, VO₂max) con **literatura científica validada** de Scopus y Web of Science para generar planes de entrenamiento adaptativos y prevenir lesiones.

El diferenciador frente a las apps genéricas: cada recomendación se construye sobre el **baseline personal** del corredor (no rangos poblacionales) y se respalda con papers citados (RCT, meta-análisis, observacional).

**Misión:** democratizar el correr seguro con IA + ciencia.

---

## Estructura del monorepo

```
liebre/
├── runner-agent/   # Backend Python — agentes + FastAPI + Postgres + Alembic
│   ├── api/        # FastAPI app (uvicorn)
│   ├── agents/     # 5 sub-agentes (fatigue, technique, plan, science, nutrition)
│   ├── memory/     # SQLAlchemy models + repositorios multitenant
│   ├── alembic/    # Migrations versionadas
│   ├── tests/      # pytest + testcontainers
│   └── infra/      # Documentación de GCP (Cloud Run, Cloud SQL, Secret Manager)
│
├── web/            # Frontend Next.js 16 (App Router + SSR + Tailwind 4)
│   ├── src/app/    # /, /dashboard
│   └── src/components/dashboard/   # HRV, Goal, Profile, Weekly cards
│
└── openspec/       # Especificaciones formales (proposal + design + tasks por change)
    └── changes/liebre-mvp/
```

---

## Stack

| Capa | Tecnología |
|---|---|
| LLM | Anthropic Claude `claude-sonnet-4-6` con prompt caching |
| Backend | Python 3.11 · FastAPI · SQLAlchemy 2 · Alembic |
| Frontend | Next.js 16 · React 19 · TypeScript · Tailwind 4 |
| DB | PostgreSQL 16 — local en Docker · prod en Cloud SQL `us-east1` |
| Auth | Firebase Auth (Google + Phone passwordless) |
| Hosting | Cloud Run (API) + Firebase App Hosting (web) |
| Secretos | Google Secret Manager (credenciales Garmin per-user) |
| Datos externos | Garmin Connect · Scopus API · Web of Science API |
| Mensajería (fase 2) | n8n self-hosted → WhatsApp Business Cloud API |

---

## Desarrollo local

```bash
# 1. Backend Python — Postgres en Docker + API en :8080
cd runner-agent
docker compose up -d
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL="postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre"
alembic upgrade head
python scripts/seed_jose_known_data.py   # datos demo de José
uvicorn api.main:app --reload --port 8080

# 2. Frontend Next.js — en :3000
cd ../web
npm install
npm run dev

# 3. Abre http://localhost:3000/dashboard
```

Documentación API en `http://localhost:8080/docs` (Swagger auto-generado).

---

## Tests

```bash
cd runner-agent
docker compose up -d
pytest                       # 23 tests (19 unit + 4 integration)
pytest --cov                 # con reporte de cobertura HTML
```

---

## Despliegue (en progreso)

| Componente | Destino | Estado |
|---|---|---|
| Frontend | Firebase App Hosting + dominio `liebre.run` | pendiente Semana 5 |
| API | Cloud Run `us-east1` | pendiente Semana 2 |
| DB | Cloud SQL `liebre-db` (Postgres 16, db-f1-micro) | ✅ provisionado |
| Secretos | Secret Manager (`postgres_*_password`, `garmin_creds_{uid}`) | ✅ configurado |
| Auth | Firebase Auth (Google + Phone) | ✅ activos |
| Identificadores | GCP project `liebre-mvp` · billing `liebre.run` | ✅ creado |

Detalles en [`runner-agent/infra/README.md`](runner-agent/infra/README.md).

---

## Documentación

- **Backend**: [`runner-agent/README.md`](runner-agent/README.md)
- **Migrations**: [`runner-agent/alembic/README.md`](runner-agent/alembic/README.md)
- **Infraestructura GCP**: [`runner-agent/infra/README.md`](runner-agent/infra/README.md)
- **Especificación formal del MVP**: [`openspec/changes/liebre-mvp/`](openspec/changes/liebre-mvp/)

---

## Principios

- **Baseline personal, no poblacional.** El agente construye el baseline HRV del corredor en sus primeras 14 noches; no usa valores de literatura como referencia individual.
- **Evidencia citada.** Toda recomendación de cambio de carga, técnica o nutrición trae el paper que la sustenta (autor, año, journal, DOI).
- **No reemplaza al médico deportivo.** El agente detecta y alerta; las decisiones clínicas siguen siendo humanas.
- **Privacidad por diseño.** Credenciales Garmin cifradas en Secret Manager (nunca en BD); endpoint de borrado total (`DELETE /v1/users/me`).

---

© 2026 Liebre
