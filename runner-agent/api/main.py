"""FastAPI app de Liebre — backend del dashboard.

Levantar en dev:
    DATABASE_URL=postgresql+psycopg2://liebre_app:liebre_dev_pw@localhost:5432/liebre \\
    .venv/bin/uvicorn api.main:app --reload --port 8080

Docs auto-generadas en:
    http://localhost:8080/docs       (Swagger UI)
    http://localhost:8080/redoc      (ReDoc)
    http://localhost:8080/openapi.json
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import activities, cronologia, dashboard, diagnosis, health, sync
from api.settings import settings

app = FastAPI(
    title="Liebre API",
    description=(
        "Backend de Liebre — agente de IA para corredores. "
        "Sirve datos de Garmin + análisis personalizado + recomendaciones "
        "respaldadas por papers científicos."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)
app.include_router(diagnosis.router, prefix=settings.api_v1_prefix)
app.include_router(cronologia.router, prefix=settings.api_v1_prefix)
app.include_router(activities.router, prefix=settings.api_v1_prefix)
app.include_router(sync.router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "service": "liebre-api",
        "environment": settings.environment,
        "docs": "/docs",
    }
