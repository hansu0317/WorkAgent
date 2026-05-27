from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "work-agent"
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
