# base.py
"""Production-grade configuration management engine.

Parses, groups, and validates all environment variables utilizing strict typing
safeguards to ensure fail-fast behaviors on invalid structural configurations.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from dotenv import load_dotenv

# Ensure environment variables are seeded from .env before validation execution
load_dotenv()


class BotSettings(BaseModel):
    """Encapsulates Telegram bot identity and communication hooks."""
    TOKEN: str = Field(..., alias="BOT_TOKEN")
    USERNAME: str = Field(..., alias="BOT_USERNAME")
    WEBHOOK_URL: Optional[str] = Field(default=None, alias="WEBHOOK_URL")

    @field_validator("TOKEN")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or ":" not in v:
            raise ValueError("Malformed BOT_TOKEN payload provided.")
        return v


class DatabaseSettings(BaseModel):
    """Manages asynchronous PostgreSQL engine connectivity profiles."""
    HOST: str = Field(..., alias="DB_HOST")
    PORT: int = Field(default=5432, alias="DB_PORT")
    NAME: str = Field(..., alias="DB_NAME")
    USER: str = Field(..., alias="DB_USER")
    PASSWORD: str = Field(..., alias="DB_PASSWORD")
    ASYNC_URL: str = Field(default="")

    @model_validator(mode="after")
    def construct_async_url(self) -> "DatabaseSettings":
        self.ASYNC_URL = (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )
        return self


class RedisSettings(BaseModel):
    """Controls parameters for state tracking caches and distributed buses."""
    HOST: str = Field(..., alias="REDIS_HOST")
    PORT: int = Field(default=6379, alias="REDIS_PORT")
    PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    DB: int = Field(default=0, alias="REDIS_DB")


class SecuritySettings(BaseModel):
    """Enforces systemic hashing, signing, and cryptography boundaries."""
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    JWT_SECRET: str = Field(..., alias="JWT_SECRET")
    ENCRYPTION_KEY: bytes = Field(..., alias="ENCRYPTION_KEY")
    PASSWORD_SALT: str = Field(..., alias="PASSWORD_SALT")

    @field_validator("ENCRYPTION_KEY", mode="before")
    @classmethod
    def cast_encryption_key(cls, v: Any) -> bytes:
        if isinstance(v, str):
            return v.encode("utf-8")
        return v


class PaymentSettings(BaseModel):
    """Configures explicit African market boundaries for the Paystack Gateway."""
    SECRET_KEY: str = Field(..., alias="PAYSTACK_SECRET_KEY")
    PUBLIC_KEY: str = Field(..., alias="PAYSTACK_PUBLIC_KEY")
    WEBHOOK_SECRET: str = Field(..., alias="PAYSTACK_WEBHOOK_SECRET")
    CURRENCY: str = "NGN"
    CURRENCY_SYMBOL: str = "₦"


class CelerySettings(BaseModel):
    """Coordinates message broker and result paths for heavy jobs queues."""
    BROKER_URL: str = Field(..., alias="CELERY_BROKER_URL")
    RESULT_BACKEND: str = Field(..., alias="CELERY_RESULT_BACKEND")


class SchedulerSettings(BaseModel):
    """Locks time expressions down explicitly to localized geo-regions."""
    TIMEZONE: str = Field(default="Africa/Lagos", alias="TIMEZONE")


class LoggingSettings(BaseModel):
    """System-wide trace parameters tracking standard storage streams."""
    LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    # BUG FIX: LOG_PATH was required (Field(...)) which causes a crash in Railway/Docker
    # environments that don't set this variable. Made optional with a sensible default.
    PATH: Path = Field(default=Path("/tmp/investment_platform/logs"), alias="LOG_PATH")

    @field_validator("PATH", mode="before")
    @classmethod
    def cast_path(cls, v: Any) -> Path:
        return Path(v)


class StorageSettings(BaseModel):
    """Defines isolated structural runtime storage block directory mappings."""
    # BUG FIX: STORAGE_PATH and BACKUP_PATH were required fields (Field(...)).
    # In Railway, these env vars are not set, causing crash at import time.
    # Defaulted to writable /tmp paths for Railway compatibility.
    STORAGE_PATH: Path = Field(default=Path("/tmp/investment_platform/storage"), alias="STORAGE_PATH")
    BACKUP_PATH: Path = Field(default=Path("/tmp/investment_platform/backups"), alias="BACKUP_PATH")

    @field_validator("STORAGE_PATH", "BACKUP_PATH", mode="before")
    @classmethod
    def cast_path(cls, v: Any) -> Path:
        return Path(v)

    @model_validator(mode="after")
    def provision_directories(self) -> "StorageSettings":
        # BUG FIX: Original code called mkdir at import time without try/except.
        # In read-only filesystems this would crash the entire application startup.
        try:
            self.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
            self.BACKUP_PATH.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # Non-fatal: log directories may be managed externally
        return self


class FeatureFlags(BaseModel):
    """Manages conditional system execution layers dynamically across scopes."""
    DEBUG: bool = Field(default=False, alias="DEBUG")
    ENABLE_WEBHOOK: bool = Field(default=False, alias="ENABLE_WEBHOOK")
    ENABLE_SCHEDULER: bool = Field(default=True, alias="ENABLE_SCHEDULER")
    ENABLE_BACKUP: bool = Field(default=True, alias="ENABLE_BACKUP")

    @field_validator("DEBUG", "ENABLE_WEBHOOK", "ENABLE_SCHEDULER", "ENABLE_BACKUP", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


class ApplicationSettings(BaseModel):
    """Root configuration aggregator unifying platform operational settings."""
    bot: BotSettings
    database: DatabaseSettings
    redis: RedisSettings
    security: SecuritySettings
    payment: PaymentSettings
    celery: CelerySettings
    scheduler: SchedulerSettings
    logging: LoggingSettings
    storage: StorageSettings
    flags: FeatureFlags


def load_settings_from_env() -> ApplicationSettings:
    """Builds, populates, and validates application settings from runtime context.

    Raises:
        RuntimeError: Evaluated when runtime validations violate invariant mappings.
    """
    raw_env: Dict[str, Any] = dict(os.environ)
    try:
        return ApplicationSettings(
            bot=BotSettings(**raw_env),
            database=DatabaseSettings(**raw_env),
            redis=RedisSettings(**raw_env),
            security=SecuritySettings(**raw_env),
            payment=PaymentSettings(**raw_env),
            celery=CelerySettings(**raw_env),
            scheduler=SchedulerSettings(**raw_env),
            logging=LoggingSettings(**raw_env),
            storage=StorageSettings(**raw_env),
            flags=FeatureFlags(**raw_env),
        )
    except ValidationError as error:
        import sys
        sys.stderr.write(f"[CRITICAL_CONFIG_ERROR] Environmental schema mismatch:\n{error}\n")
        raise RuntimeError("Fatal system initialization trace failure.") from error


# Global single instance instantiation pattern
settings: ApplicationSettings = load_settings_from_env()
