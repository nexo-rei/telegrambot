# system.py
"""Shared Non-Financial System Invariants Matrix.

Defines the authoritative application layout constraints, Telegram protocol bounds,
security token lifetimes, caching namespaces, background worker thread pools, and
infrastructure timeouts. Centralizes non-fiscal configurations to maintain structural
consistency and prevent magic-number usage throughout the enterprise architecture.
"""

import zoneinfo
from dataclasses import dataclass
from enum import Enum, unique
from typing import Final, Optional


# --- Core Application Metadata ---
APP_NAME: Final[str] = "Velorix Enterprise Investment Core"
APP_VERSION: Final[str] = "2.0.0"
BUILD_VERSION: Final[str] = "2026.06.27.01"
PLATFORM_NAME: Final[str] = "Velorix"
DEFAULT_THEME: Final[str] = "PREMIUM_DARK_LUXURY"

# --- Internationalization & Chronology ---
PLATFORM_TIMEZONE: Final[str] = "Africa/Lagos"
DEFAULT_LOCALE: Final[str] = "en_NG"
SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en_NG", "en_US")


# --- Telegram Protocol Specification Boundaries ---
MAX_MESSAGE_LENGTH_BYTES: Final[int] = 4096
MAX_CAPTION_LENGTH_BYTES: Final[int] = 1024
MAX_CALLBACK_DATA_BYTES: Final[int] = 64
MAX_KEYBOARD_BUTTONS_PER_ROW: Final[int] = 8
DEFAULT_PARSE_MODE_CODE: Final[str] = "HTML"
DEFAULT_PAGE_SIZE_LIMIT: Final[int] = 10
DEFAULT_PAGINATION_LIMIT: Final[int] = 50
DEFAULT_EDIT_TIMEOUT_SECONDS: Final[int] = 172800  # 48 Hours


# --- Identity & Lifecycle Configurations ---
USER_SESSION_TTL_SECONDS: Final[int] = 86400  # 24 Hours
LOGIN_FLOW_TIMEOUT_SECONDS: Final[int] = 300
OTP_EXPEXPIRATION_SECONDS: Final[int] = 120
MAX_CONCURRENT_DEVICES_PER_USER: Final[int] = 3
MIN_USERNAME_LENGTH: Final[int] = 5
MAX_USERNAME_LENGTH: Final[int] = 32
MAX_DISPLAY_NAME_LENGTH: Final[int] = 64
MAX_BIOGRAPHY_LENGTH: Final[int] = 160


# --- Security Hardening Matrices ---
PASSWORD_HASH_ALGORITHM: Final[str] = "argon2id"
TOKEN_EXPIRATION_SECONDS: Final[int] = 900  # 15 Minutes
REFRESH_TOKEN_LIFETIME_DAYS: Final[int] = 30
MAX_LOGIN_ATTEMPTS_BEFORE_LOCKOUT: Final[int] = 5
LOCKOUT_DURATION_SECONDS: Final[int] = 1800  # 30 Minutes
CSRF_LIFETIME_SECONDS: Final[int] = 3600
SECURE_COOKIE_SAMESITE: Final[str] = "Lax"


# --- Infrastructure Cache Storage Parameters ---
DEFAULT_CACHE_TTL_SECONDS: Final[int] = 3600  # 1 Hour
SESSION_CACHE_TTL_SECONDS: Final[int] = 86400
NAVIGATION_CACHE_TTL_SECONDS: Final[int] = 1800
KEYBOARD_CACHE_TTL_SECONDS: Final[int] = 7200
MESSAGE_CACHE_TTL_SECONDS: Final[int] = 604800  # 7 Days
REDIS_NAMESPACE_PREFIX: Final[str] = "velorix:"
MAX_CACHE_ENTRIES_CAP: Final[int] = 50000


# --- System Observability & Logging Structural Targets ---
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
LOG_ROTATION_SIZE_BYTES: Final[int] = 10485760  # 10 MB
LOG_RETENTION_DAYS_COUNT: Final[int] = 90
ERROR_LOG_FILE_PATH: Final[str] = "logs/error.log"
SECURITY_LOG_FILE_PATH: Final[str] = "logs/security.log"
AUDIT_LOG_FILE_PATH: Final[str] = "logs/audit.log"


# --- Background Worker & Scheduling Fabrics ---
WORKER_CONCURRENCY_POOL_SIZE: Final[int] = 8
QUEUE_TIMEOUT_SECONDS: Final[int] = 5
MAX_WORKER_RETRY_ATTEMPTS: Final[int] = 5
WORKER_RETRY_DELAY_SECONDS: Final[int] = 10
SCHEDULER_INTERVAL_SECONDS: Final[int] = 60
CLEANUP_INTERVAL_SECONDS: Final[int] = 3600
HEALTH_CHECK_INTERVAL_SECONDS: Final[int] = 30


# --- Network & Execution I/O Timeout Bounds ---
API_TIMEOUT_SECONDS: Final[float] = 10.0
DATABASE_TIMEOUT_SECONDS: Final[float] = 5.0
REDIS_TIMEOUT_SECONDS: Final[float] = 3.0
WEBHOOK_TIMEOUT_SECONDS: Final[float] = 15.0
REQUEST_TIMEOUT_SECONDS: Final[float] = 12.0
MAX_CONCURRENT_TASKS_LIMIT: Final[int] = 500


@unique
class ExecutionEnvironment(str, Enum):
    """Authoritative platform environment deployment tier tokens."""
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


@dataclass(frozen=True)
class SystemValidationResult:
    """Immutable data frame conveying structural outcome traces from system parameter validation checks."""
    is_valid: bool
    error_message: Optional[str] = None


# --- Configuration In-Line Validation Helpers ---

def validate_environment_scope(env_string: str) -> SystemValidationResult:
    """Validates the active environment token deployment configuration matches legal tiers."""
    sanitized = env_string.strip().upper()
    if sanitized not in [member.value for member in ExecutionEnvironment]:
        return SystemValidationResult(
            is_valid=False,
            error_message=f"Unsupported deployment profile: '{env_string}'. Use LOCAL, DEVELOPMENT, STAGING, or PRODUCTION."
        )
    return SystemValidationResult(is_valid=True)


def validate_locale_code(locale_string: str) -> SystemValidationResult:
    """Validates if the specified language/locale tag is supported by platform catalogs."""
    if locale_string not in SUPPORTED_LOCALES:
        return SystemValidationResult(
            is_valid=False,
            error_message=f"Unsupported locale specification: '{locale_string}'. Supported profiles: {SUPPORTED_LOCALES}."
        )
    return SystemValidationResult(is_valid=True)


def validate_platform_timezone(timezone_string: str) -> SystemValidationResult:
    """Validates that a string matches a recognized, system-parsable IANA timezone identification code."""
    try:
        zoneinfo.ZoneInfo(timezone_string)
        return SystemValidationResult(is_valid=True)
    except Exception:
        return SystemValidationResult(
            is_valid=False,
            error_message=f"Invalid or unrecognized IANA structural timezone designation signature: '{timezone_string}'."
        )
