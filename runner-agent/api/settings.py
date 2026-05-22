"""Configuración tipada via Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la API leída del entorno / .env."""

    environment: str = "dev"  # dev | staging | prod
    api_v1_prefix: str = "/v1"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "https://liebre.run",
    ]

    # Auth — en dev se bypassa con dev_user_id
    dev_user_id: str = "jose_dev_uid"
    firebase_project_id: str = "liebre-mvp"

    # GCP
    gcp_project_id: str = "liebre-mvp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_dev(self) -> bool:
        return self.environment == "dev"


settings = Settings()
