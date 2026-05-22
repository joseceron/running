# Alembic migrations — Liebre

Versionado del schema Postgres. **Toda** modificación al schema debe ir por aquí.

## Workflow estándar

```bash
# 1. Editar memory/models.py
# 2. Generar migration automática (compara modelos vs DB actual)
alembic revision --autogenerate -m "descripcion breve en presente"

# 3. Revisar el archivo generado en alembic/versions/ — Alembic no es perfecto
#    con índices/constraints; ajustar manualmente si hace falta

# 4. Aplicar a tu DB local
alembic upgrade head

# 5. Commit del archivo de migration al repo
```

## Comandos útiles

```bash
alembic current                       # revisión actual de la DB
alembic history                       # historial de revisiones
alembic upgrade head                  # aplicar todas las pendientes
alembic upgrade +1                    # aplicar solo la siguiente
alembic downgrade -1                  # rollback de la última
alembic downgrade base                # rollback total (vaciar schema)
alembic stamp head                    # marcar como aplicada SIN ejecutar (post-bootstrap)
alembic upgrade head --sql            # imprimir SQL sin aplicar (offline)
```

## Convenciones del proyecto

- Cada migration debe ser **idempotente**: si la corres dos veces, no rompe.
- Cambios destructivos (DROP, rename) → migration separada, nunca mezclar con adds.
- Datos: usar `op.execute(...)` solo si es estrictamente necesario; preferir
  scripts separados en `scripts/`.
- Naming: `<YYYYMMDD>_<seq4>_<snake_case_msg>.py` se genera automático.

## En producción

```bash
# Antes de cada deploy de la API, correr migrations contra Cloud SQL
DATABASE_URL="postgresql+psycopg2://liebre_app:...@/liebre?host=/cloudsql/..." \
  alembic upgrade head
```

El Dockerfile incluye un `alembic upgrade head` en el entrypoint? **NO** — se hace como
job separado en Cloud Build/CI para evitar carreras entre múltiples instancias de
Cloud Run que arranquen simultáneamente.
