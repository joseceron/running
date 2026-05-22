# Runner Agent — núcleo de Liebre

Agente de IA personalizado para corredores. Analiza datos reales de Garmin (HRV, running dynamics, Body Battery) y los combina con literatura científica (Scopus + Web of Science) para generar planes de entrenamiento adaptativos.

Este paquete contiene dos sistemas conviviendo en paralelo:

| Sistema | Estado | Uso |
|---|---|---|
| **Personal (legacy)** — SQLite single-tenant en `memory/db.py` + `memory/runner_profile.py` | Activo en producción para José | `python main.py daily` (sin cambios) |
| **Liebre SaaS (nuevo)** — Postgres multitenant en `memory/models.py` + `memory/repositories/` + Alembic | En construcción semana 1 | Backend de la API FastAPI (próximo) |

El cutover del legacy al nuevo se hace cuando la API esté desplegada (Semana 4-5). Mientras tanto, ambos coexisten y el sistema viejo no se rompe.

## Setup desarrollo (sistema nuevo)

```bash
# 1. Levantar Postgres local
docker compose up -d

# 2. Crear/activar venv e instalar deps de desarrollo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 3. Variable de entorno (añadir al .env o exportar)
export DATABASE_URL="postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre"

# 4. Aplicar migrations
alembic upgrade head

# 5. Correr tests
pytest                           # todos
pytest tests/unit/               # solo unit
pytest -m "not integration"      # excluir tests con testcontainers
pytest --cov                     # con reporte de cobertura
```

## Migrations (Alembic)

**Toda modificación al schema** pasa por una migration versionada en `alembic/versions/`. Workflow:

```bash
# Tras editar memory/models.py:
alembic revision --autogenerate -m "descripcion breve"
# Revisar el archivo generado (Alembic no es perfecto con índices/checks)
alembic upgrade head

# Otros comandos:
alembic current            # revisión actual de la DB
alembic history            # historial
alembic downgrade -1       # rollback de la última
```

Detalles en [`alembic/README.md`](alembic/README.md).

El test `test_models_match_migrations` falla en CI si alguien edita modelos sin generar la migration → no se puede mergear schema drift.

## Tests

Stack: **pytest + testcontainers + pytest-cov**.

```bash
pytest                           # todos
pytest tests/unit/test_models.py # un archivo
pytest -k "isolation" -v         # por keyword
pytest --cov --cov-report=html   # cobertura HTML en .coverage_html/
```

Markers definidos:
- `unit` — tests sobre Postgres del docker-compose
- `integration` — tests que levantan Postgres efímero con testcontainers
- `slow` — tests >2s

Fixtures clave en `tests/conftest.py`:
- `db_session`: transacción savepoint que se rollback al final del test
- `user_a` / `user_b`: dos usuarios preinsertados para validar aislamiento

## Configuración del .env (sistema legacy de José)

```bash
python bootstrap_env.py    # copia desde /Users/jose.ceron/Documents/emira/.env
```

Variables (sistema legacy):
```
GARMIN_EMAIL
GARMIN_PASSWORD
SCOPUS_API_KEY
WOS_API_KEY
ANTHROPIC_API_KEY
DATABASE_URL=sqlite:///runner_agent.db
MORNING_CHECK_TIME=07:00
```

Variables adicionales del sistema nuevo (Liebre SaaS):
```
GCP_PROJECT_ID=liebre-mvp
DATABASE_URL=postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre  # dev
# (en Cloud Run el DATABASE_URL apunta al socket Unix de Cloud SQL Auth Proxy)
```

## Comandos disponibles (sistema legacy)

```bash
python main.py daily      # Revisión matutina (HRV, Body Battery, plan del día)
python main.py post-run   # Análisis post-entrenamiento (técnica, ACWR)
python main.py weekly     # Revisión semanal + plan siguiente semana
python main.py schedule   # Inicia scheduler automático (MORNING_CHECK_TIME)
python main.py init       # Inicializa la base de datos SQLite
```

## Migración del SQLite al Postgres multitenant

Cuando José se registre en `liebre.run` por primera vez, su SQLite local se importa al Postgres con su Firebase UID:

```bash
python scripts/migrate_sqlite_to_postgres.py \
  --sqlite ./runner_agent.db \
  --user-id <FIREBASE_UID_DE_JOSE>
```

El script es idempotente — se puede re-correr.

## Estructura del repo

```
runner-agent/
├── data/
│   ├── garmin_client.py    # Wrapper Garmin Connect (legacy + se refactoriza per-user)
│   ├── scopus_client.py    # Scopus API con caché
│   └── wos_client.py       # Web of Science API con caché
├── agents/
│   ├── orchestrator.py     # Agente Claude (claude-sonnet-4-6) con tool use
│   ├── fatigue_agent.py    # HRV vs baseline personal + ACWR
│   ├── technique_agent.py  # Cadencia, GCT, degradación de forma
│   ├── plan_agent.py       # Plan semanal adaptativo
│   ├── science_agent.py    # Búsqueda y clasificación de papers
│   └── nutrition_agent.py  # Balance calórico y alerta proteica
├── memory/                 # ← contiene ambos sistemas
│   ├── db.py               # ⚠️ legacy SQLite (se mantiene durante migración)
│   ├── runner_profile.py   # ⚠️ legacy
│   ├── database.py         # 🆕 SQLAlchemy engine + session_scope
│   ├── models.py           # 🆕 ORM models multitenant con user_id
│   └── repositories/       # 🆕 queries por entidad (users, hrv, weekly, ...)
├── alembic/                # 🆕 migrations versionadas
│   ├── env.py
│   └── versions/
├── tests/                  # 🆕 pytest + testcontainers
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── scripts/                # 🆕 utilidades (migración SQLite→Postgres, etc.)
├── infra/                  # 🆕 docs de infra GCP/Firebase
├── scheduler/
│   └── daily_check.py      # APScheduler para ciclo matutino (legacy)
├── reports/
│   └── weekly_report.py    # Formateador de reportes
├── alembic.ini
├── docker-compose.yml      # 🆕 Postgres 16 para dev local
├── pyproject.toml          # 🆕 pytest, ruff, mypy config
├── requirements.txt
├── requirements-dev.txt    # 🆕 pytest, testcontainers, mypy, ruff
└── main.py                 # CLI principal (legacy)
```

## Por qué 14 días para baseline HRV

El sistema requiere **mínimo 14 días de datos HRV** antes de emitir recomendaciones de carga basadas en HRV. El HRV varía enormemente entre individuos; los rangos poblacionales (ej. "HRV normal: 20–80 ms") no tienen validez individual. Tu baseline real es el único referente útil.

Mientras hay <14 días: `⚠️ Baseline HRV en construcción: N/14 días disponibles`.

## Verificación end-to-end (lo que ya funciona)

```bash
docker compose up -d
export DATABASE_URL="postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre"
alembic upgrade head
pytest tests/ -v
# → 19 unit + 4 integration = 23 tests passed
```
