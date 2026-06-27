# security.py
"""Security Configuration Engine.

Consolidates, structures, and enforces cryptography parameters, perimeter defenses,
anti-brute-force thresholds, and Paystack/Telegram signing verification keys.
"""

from typing import Any, Dict, List
from config.base import settings


class SecurityConfig:
    """Production-ready cryptographic and system perimeter protection settings.

    Defines execution metrics for token verification, payload structural signed 
    authenticity checks, and structural rate-limiting thresholds to prevent
    fraudulent operations.
    """

    # 1. Core Secrets and Symmetric Signing Definitions
    SECRET_KEY: str = settings.security.SECRET_KEY
    JWT_SECRET: str = settings.security.JWT_SECRET
    ENCRYPTION_KEY: bytes = settings.security.ENCRYPTION_KEY
    PASSWORD_SALT: str = settings.security.PASSWORD_SALT

    # 2. Cryptographic Algorithm Selections
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    JWT_SIGNING_ALGORITHM: str = "HS256"

    # 3. Structural Token Lifespans and Session Rules
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_EXPIRATION_SECONDS: int = 3600  # 1 hour absolute token validity window
    ACCOUNT_LOCK_DURATION_SECONDS: int = 1800  # 30 minutes cooling-off lock boundary

    # 4. Anti-Brute-Force & Perimeter Gatekeeping Thresholds
    MAX_LOGIN_ATTEMPTS: int = 5
    MAX_AUTHENTICATION_RETRIES: int = 3
    RATE_LIMIT_BURST_CEILING: int = 10
    RATE_LIMIT_WINDOW_SECONDS: float = 1.0

    # 5. Financial Vendor Integration Signatures (Paystack Specifics)
    PAYSTACK_WEBHOOK_SECRET: str = settings.payment.WEBHOOK_SECRET
    PAYSTACK_SIGNATURE_HEADER: str = "x-paystack-signature"

    # 6. Gateway IP Whitelisting Infrastructure Boundaries
    # Explicitly matches regional Paystack processing nodes for hard execution boundaries
    TRUSTED_IP_WHITELIST: List[str] = [
        "52.31.139.46",
        "52.49.173.169",
        "52.214.14.220"
    ]
    
    TRUSTED_HOSTS: List[str] = [
        "api.paystack.co",
        "api.telegram.org"
    ]

    # 7. Enterprise API Interface Stubs (CORS / CSRF / Secure Web Cookie Targets)
    HTTP_SECURE_HEADERS: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self';",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload"
    }

    HTTP_COOKIE_RULES: Dict[str, Any] = {
        "httponly": True,
        "secure": True,
        "samesite": "Strict",
        "domain": None
    }

    CORS_ALLOWED_ORIGINS: List[str] = []
    CSRF_TIME_TO_LIVE_SECONDS: int = 3600

    # 8. Forensic Telemetry Security Logging Profiles
    SECURITY_LOGGING_OPTIONS: Dict[str, Any] = {
        "log_payload_on_tamper": True,
        "mask_sensitive_fields": ["password", "token", "secret", "cvv", "card"],
        "emit_critical_syslog_on_lockout": True
    }

    @classmethod
    def get_crypto_context_parameters(cls) -> Dict[str, Any]:
        """Exposes raw architectural operational state configurations for cryptography factory binding."""
        return {
            "algorithm": cls.PASSWORD_HASH_ALGORITHM,
            "rounds": 12,
            "salt_length": 16
        }

    @classmethod
    def get_jwt_encoding_meta(cls) -> Dict[str, Any]:
        """Provides dynamic tracking arrays mapping structural signatures validation bounds."""
        return {
            "secret": cls.JWT_SECRET,
            "algorithm": cls.JWT_SIGNING_ALGORITHM,
            "expiration_delta_minutes": cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        }
        
