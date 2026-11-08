"""Typed application settings loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    Values come from environment variables or a local ``.env`` file. Field names
    map case-insensitively, so ``app_name`` reads ``APP_NAME``.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "ResumeRadar"
    app_base_url: str = "http://localhost:8000"
    frontend_origin: str = "http://localhost:5173"

    database_url: str = "sqlite:///./data/resume_radar.db"

    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"

    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "resume-radar/0.1"

    github_token: str | None = None

    cache_ttl_seconds: int = 86400
    max_upload_mb: int = 10

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance so config is read only once."""
    return Settings()
