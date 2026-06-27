# account_roles.py
"""Account-related Enumerations.

Defines the core security, role, and verification state machines for user 
accounts and administrative access. These enumerations enforce strict 
access control, compliance tracking (KYC/AML), and session management 
integrity across the platform.
"""

from enum import StrEnum, auto


class UserRole(StrEnum):
    USER = auto()
    VIP = auto()
    MODERATOR = auto()
    ADMINISTRATOR = auto()
    SUPER_ADMINISTRATOR = auto()
    SYSTEM = auto()


class AccountStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    SUSPENDED = auto()
    FROZEN = auto()
    DISABLED = auto()
    CLOSED = auto()
    DELETED = auto()


class VerificationStatus(StrEnum):
    UNVERIFIED = auto()
    PENDING = auto()
    VERIFIED = auto()
    REJECTED = auto()


class KYCStatus(StrEnum):
    NOT_STARTED = auto()
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class AMLStatus(StrEnum):
    CLEAR = auto()
    UNDER_REVIEW = auto()
    FLAGGED = auto()
    RESTRICTED = auto()


class AuthenticationProvider(StrEnum):
    TELEGRAM = auto()
    ADMIN_PANEL = auto()
    API = auto()


class AuthenticationStatus(StrEnum):
    AUTHENTICATED = auto()
    PENDING = auto()
    EXPIRED = auto()
    REVOKED = auto()


class SessionStatus(StrEnum):
    ACTIVE = auto()
    EXPIRED = auto()
    REVOKED = auto()
    LOGGED_OUT = auto()


class PermissionScope(StrEnum):
    READ = auto()
    WRITE = auto()
    UPDATE = auto()
    DELETE = auto()
    MODERATE = auto()
    ADMIN = auto()
    SUPER_ADMIN = auto()
    SYSTEM = auto()


class AdminRole(StrEnum):
    SUPPORT = auto()
    FINANCE = auto()
    SECURITY = auto()
    SUPERVISOR = auto()


class ModeratorRole(StrEnum):
    COMMUNITY = auto()
    CONTENT = auto()
    TICKET = auto()


class UserTier(StrEnum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()
    PLATINUM = auto()
    DIAMOND = auto()


class SecurityLevel(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class RiskLevel(StrEnum):
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class DeviceTrustLevel(StrEnum):
    TRUSTED = auto()
    UNKNOWN = auto()
    SUSPICIOUS = auto()
    BLOCKED = auto()
