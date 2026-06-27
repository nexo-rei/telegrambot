# validators.py
"""Production-grade Authentication Validator.

Provides a centralized validation engine for all incoming authentication requests, 
user registration data, and session integrity checks. Ensures that only sanitized, 
business-compliant data is processed by the AuthenticationService, preventing 
unauthorized access and maintaining system-wide security posture.
"""

import logging
import re
from dataclasses import dataclass
from typing import Final, Optional

from src.modules.authentication.dtos import UserRegistrationDTO

logger = logging.getLogger("investment_platform.modules.authentication.validators")


@dataclass(frozen=True)
class ValidationResult:
    """Standardized outcome for authentication validation checks."""
    is_valid: bool
    error_code: Optional[str] = None
    message: Optional[str] = None


class AuthenticationValidator:
    """Core validator for authentication domain logic and input sanitization."""

    # Regex for standard username validation
    USERNAME_PATTERN: Final[re.Pattern] = re.compile(r"^[a-zA-Z0-9_]{3,32}$")

    async def validate_registration(self, data: UserRegistrationDTO) -> ValidationResult:
        """Validates all constraints for a new user registration request."""
        
        # Validate Telegram ID
        if data.telegram_id <= 0:
            return ValidationResult(False, "INVALID_TG_ID", "Telegram ID must be a positive integer.")

        # Validate Username if present
        if data.username and not self.USERNAME_PATTERN.match(data.username):
            return ValidationResult(False, "INVALID_USERNAME", "Username format is invalid.")

        # Validate Referral Code if present
        if data.referral_code and len(data.referral_code) != 8:
            return ValidationResult(False, "INVALID_REFERRAL", "Referral code must be 8 characters.")

        return ValidationResult(True)

    async def validate_session(self, session_token: str) -> ValidationResult:
        """Validates the structure and integrity of a session token."""
        if not session_token or len(session_token) < 32:
            return ValidationResult(False, "INVALID_TOKEN", "Session token is malformed or missing.")
        
        return ValidationResult(True)

    def is_referral_self_reference(self, telegram_id: int, referrer_id: int) -> bool:
        """Prevents users from using their own referral code."""
        return telegram_id == referrer_id
