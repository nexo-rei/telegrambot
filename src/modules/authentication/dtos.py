# dtos.py
"""Production-grade Authentication Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing authentication
and user-related data across the service boundary. These DTOs facilitate safe 
serialization and communication between the presentation, service, and data layers.
"""

from dataclasses import dataclass
from typing import Final, Optional


@dataclass(frozen=True)
class UserRegistrationDTO:
    """Represents the request data required to register a new platform user."""
    telegram_id: int
    phone_number: str
    username: Optional[str] = None
    referral_code: Optional[str] = None
    language_code: str = "en"


@dataclass(frozen=True)
class UserRegistrationResponse:
    """Represents the outcome of a user registration attempt."""
    user_id: int
    telegram_id: int
    is_success: bool
    message: str


@dataclass(frozen=True)
class SessionContext:
    """Immutable snapshot of an active user session."""
    user_id: int
    telegram_id: int
    session_token: str
    vip_level: int
    is_active: bool


@dataclass(frozen=True)
class ReferralDTO:
    """Represents referral network information for a user."""
    referral_code: str
    referrer_id: Optional[int] = None
    referral_count: int = 0


@dataclass(frozen=True)
class AccountRecoveryDTO:
    """DTO for handling account recovery requests."""
    telegram_id: int
    recovery_reason: str
    timestamp: float
