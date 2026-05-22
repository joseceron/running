# Dockerfile multi-stage para liebre-api en Cloud Run
# Python 3.11-slim, FastAPI + uvicorn + dependencias del agente.

# ─── STAGE 1: builder ───────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Dependencias del sistema necesarias para psycopg2-binary (libpq) y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ─── STAGE 2: runtime ───────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    PORT=8080

WORKDIR /app

# libpq runtime (NO el -dev) + clientes mínimos
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar deps instaladas del builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la app (lo mínimo necesario para correr la API)
COPY api/        ./api/
COPY agents/     ./agents/
COPY data/       ./data/
COPY memory/     ./memory/
COPY scripts/    ./scripts/
COPY alembic/    ./alembic/
COPY alembic.ini ./

EXPOSE 8080

# Cloud Run inyecta PORT — uvicorn debe escuchar en $PORT
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
