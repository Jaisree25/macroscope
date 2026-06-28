"""Process settings from env (.env.example documents the keys).

Secrets live here, never in code or prompts (design §11).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATA_PLANE_", env_file=".env", extra="ignore")

    # Store — backend key selects the Store implementation (store/__init__.py:make_store).
    store_backend: str = "postgres"
    database_url: str = "postgresql://macro:macro@localhost:5432/macro_watcher"

    # Sources
    fred_api_key: str = ""

    # Ingestion cadence (seconds)
    fred_poll_interval: int = 3600
    gdelt_poll_interval: int = 900


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — import this, don't construct Settings directly."""
    return Settings()
