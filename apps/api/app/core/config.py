from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Chrome Hearts Price Intelligence"
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    database_url: str = Field(
        default="postgresql+psycopg://chromehearts:chromehearts@localhost:5432/chromehearts",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    admin_token: str = Field(default="change-me", alias="ADMIN_TOKEN")
    admin_session_secret: str = Field(default="change-me-too", alias="ADMIN_SESSION_SECRET")
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")
    object_storage_bucket: str | None = Field(default=None, alias="OBJECT_STORAGE_BUCKET")
    artifact_storage_root: str = Field(default=".artifacts", alias="ARTIFACT_STORAGE_ROOT")
    submission_upload_root: str = Field(default=".uploads", alias="SUBMISSION_UPLOAD_ROOT")
    asset_preview_max_bytes: int = Field(default=262_144, alias="ASSET_PREVIEW_MAX_BYTES")
    upload_max_mb: int = Field(default=8, alias="UPLOAD_MAX_MB")
    ebay_enabled: bool = Field(default=True, alias="EBAY_ENABLED")
    rinkan_enabled: bool = Field(default=True, alias="RINKAN_ENABLED")
    reddit_enabled: bool = Field(default=False, alias="REDDIT_ENABLED")
    stockx_enabled: bool = Field(default=False, alias="STOCKX_ENABLED")


@lru_cache
def get_settings() -> Settings:
    return Settings()
