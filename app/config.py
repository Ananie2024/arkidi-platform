"""
Arkidi Platform Application Configuration
Archdiocese of Kigali Digital Archive & Parish Management System
"""
from typing import List, Optional
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application & Environment
    # ------------------------------------------------------------------
    APP_NAME: str = Field(default="Arkidi Platform API")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    # ------------------------------------------------------------------
    # Database Configuration (PostgreSQL + PostGIS)
    # ------------------------------------------------------------------
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="arkidi_db")
    DATABASE_USER: str = Field(default="arkidi_user")
    DATABASE_PASSWORD: str = Field(default="arkidi_secure_password_dev_2026")
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> str:
        """Synchronous connection string (used for Alembic or sync scripts)."""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Async connection string for asyncpg + SQLAlchemy 2.0."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # ------------------------------------------------------------------
    # Security & Authentication
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(
        default="super_secure_arkidi_platform_archdiocese_of_kigali_secret_key_32bytes_min"
    )

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:8000", "http://localhost:3000"]
    )

    # ------------------------------------------------------------------
    # Redis & Caching
    # ------------------------------------------------------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    SECURITY_CRITICAL_MODE: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Celery Background Tasks
    # ------------------------------------------------------------------
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    # ------------------------------------------------------------------
    # File Storage & Archival
    # ------------------------------------------------------------------
    FILE_STORAGE_PATH: str = Field(default="./file-storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"]
    )
    BACKUP_BASE_PATH: str = Field(default="./backups")
    GCS_ENABLED: bool = Field(default=False)
    GCS_PROJECT_ID: Optional[str] = Field(default=None)
    GCS_BUCKET_NAME: Optional[str] = Field(default=None)
    GCS_CREDENTIALS_PATH: Optional[str] = Field(default=None)
    B2_ENABLED: bool = Field(default=False)
    B2_ACCOUNT_ID: Optional[str] = Field(default=None)
    B2_APPLICATION_KEY: Optional[str] = Field(default=None)
    B2_BUCKET_NAME: Optional[str] = Field(default=None)

    # ------------------------------------------------------------------
    # Internationalization (i18n)
    # ------------------------------------------------------------------
    DEFAULT_LANGUAGE: str = Field(default="en")
    SUPPORTED_LANGUAGES: List[str] = Field(default=["en", "fr", "rw"])

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="./logs/arkidi.log")
    LOG_MAX_BYTES: int = Field(default=10_485_760)
    LOG_BACKUP_COUNT: int = Field(default=5)


settings = Settings()
