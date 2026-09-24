"""
Arkidi Platform Application Configuration
Archdiocese of Kigali Digital Archive & Parish Management System
"""

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
    # DATABASE_PASSWORD is REQUIRED (no default) — a hardcoded credential would be
    # checked into the repository and reused across environments. Supply it via
    # .env or the environment.
    DATABASE_PASSWORD: str
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)

    # Optional *privileged* database role used ONLY for provisioning steps that a
    # non-superuser application role cannot perform itself, namely:
    #   * `CREATE EXTENSION postgis` in a freshly created scratch database
    #     (PostGIS is a non-trusted extension, so only a superuser / extension
    #     owner can create it), and
    #   * granting the application role CREATE/USAGE on the ``public`` schema of
    #     that database so a restore or migration can create its own objects.
    #
    # When the configured DATABASE_USER is itself a superuser (the default for
    # the official postgis/postgis Docker image and for simple local setups),
    # these default to the application credentials and no extra configuration is
    # required. In a production-realistic non-superuser deployment, set these to
    # the DBA/superuser role (e.g. the container's `postgres` account).
    DATABASE_ADMIN_USER: str | None = Field(default=None)
    DATABASE_ADMIN_PASSWORD: str | None = Field(default=None)

    @property
    def effective_admin_user(self) -> str:
        return self.DATABASE_ADMIN_USER or self.DATABASE_USER

    @property
    def effective_admin_password(self) -> str:
        return self.DATABASE_ADMIN_PASSWORD or self.DATABASE_PASSWORD

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> str:  # noqa: N802 - mirrors the env var / Settings name
        """Synchronous connection string (used for Alembic or sync scripts)."""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def ASYNC_DATABASE_URL(self) -> str:  # noqa: N802 - mirrors the env var / Settings name
        """Async connection string for asyncpg + SQLAlchemy 2.0."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # ------------------------------------------------------------------
    # Security & Authentication
    # ------------------------------------------------------------------
    # SECRET_KEY is intentionally REQUIRED (no default). A hardcoded/published
    # value here would silently sign real JWTs with a known secret, so the app
    # must fail to start until a real key is provided via .env or the
    # environment. Generate one with:  openssl rand -hex 32
    SECRET_KEY: str

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    RATE_LIMIT_LOGIN: str = Field(default="10/minute")
    RATE_LIMIT_REFRESH: str = Field(default="20/minute")
    RATE_LIMIT_GOOGLE_AUTH: str = Field(default="10/minute")

    # ------------------------------------------------------------------
    # Google OAuth 2.0
    # ------------------------------------------------------------------
    GOOGLE_CLIENT_ID: str | None = Field(default=None)
    GOOGLE_CLIENT_SECRET: str | None = Field(default=None)
    GOOGLE_REDIRECT_URI: str | None = Field(default=None)
    GOOGLE_ALLOW_SELF_REGISTRATION: bool = Field(default=False)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
        ]
    )
    # Optional extra regex of allowed origins (e.g. any localhost dev port).
    # Keep empty/None in production and rely on the explicit CORS_ORIGINS list.
    CORS_ORIGIN_REGEX: str | None = Field(default=None)

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
    # OCR (Tesseract) — Scanned Canonical Registers
    # ------------------------------------------------------------------
    # The archive OCR worker (app.tasks.archive_ocr) runs the real Tesseract
    # engine over scanned ledger page images so the digital archive becomes
    # full-text searchable beyond metadata. Set OCR_ENABLED=false on hosts
    # where the tesseract binary cannot be installed; the task then degrades
    # to indexing any pre-attached OCR text without extraction.
    OCR_ENABLED: bool = Field(default=True)
    # Tesseract language pack(s); requires the matching tesseract-ocr-<lang>
    # system package to be installed on the worker image.
    OCR_LANGUAGE: str = Field(default="eng+fra")
    OCR_DPI: int = Field(default=300)
    OCR_TIMEOUT_SECONDS: int = Field(default=120)

    # ------------------------------------------------------------------
    # File Storage & Archival
    # ------------------------------------------------------------------
    FILE_STORAGE_PATH: str = Field(default="./file-storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    ALLOWED_EXTENSIONS: list[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"]
    )
    BACKUP_BASE_PATH: str = Field(default="./backups")
    GCS_ENABLED: bool = Field(default=False)
    GCS_PROJECT_ID: str | None = Field(default=None)
    GCS_BUCKET_NAME: str | None = Field(default=None)
    GCS_CREDENTIALS_PATH: str | None = Field(default=None)
    B2_ENABLED: bool = Field(default=False)
    B2_ACCOUNT_ID: str | None = Field(default=None)
    B2_APPLICATION_KEY: str | None = Field(default=None)
    B2_BUCKET_NAME: str | None = Field(default=None)

    # ------------------------------------------------------------------
    # Internationalization (i18n)
    # ------------------------------------------------------------------
    DEFAULT_LANGUAGE: str = Field(default="en")
    SUPPORTED_LANGUAGES: list[str] = Field(default=["en", "fr", "rw"])

    # ------------------------------------------------------------------
    # Email / SMTP Notifications
    # ------------------------------------------------------------------
    SMTP_SERVER: str | None = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    EMAIL_SENDER: str | None = Field(default="noreply@archidiocesekigali.org")
    # Comma-separated list of recipients for backup / restore-drill failure
    # alerts.  When empty, alerts fall back to EMAIL_SENDER.
    ALERT_RECIPIENTS: str | None = Field(default=None)

    # ------------------------------------------------------------------
    # Public front-end & password reset
    # ------------------------------------------------------------------
    # Base URL of the SPA used to build self-service reset links (also used by
    # any other user-facing e-mail that links back into the frontend).
    PUBLIC_FRONTEND_URL: str = Field(default="http://localhost:5173")
    # Lifetime of one password-reset token (single-use, stored in Redis).
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="./logs/arkidi.log")
    LOG_MAX_BYTES: int = Field(default=10_485_760)
    LOG_BACKUP_COUNT: int = Field(default=5)


settings = Settings()  # type: ignore[call-arg]  # values come from the environment
