# scopes.py
"""Centralized Permission Scopes and Role-Based Access Control Definitions.

Defines the exhaustive taxonomy of system permissions, administrative roles, and 
the hierarchical mappings that govern platform access. Acts as the single 
source of truth for authorization logic across all financial, operational, 
and administrative modules.
"""

from enum import Enum, auto
from typing import Final, Mapping


class UserRole(Enum):
    """Enumeration of system-wide security roles."""
    GUEST = auto()
    REGISTERED = auto()
    VIP = auto()
    MODERATOR = auto()
    ADMIN = auto()
    SUPER_ADMIN = auto()


class PermissionScope(Enum):
    """Granular permission definitions categorized by functional domain."""
    
    # Wallet / Finance
    WALLET_VIEW = "wallet.view"
    WALLET_DEPOSIT = "wallet.deposit"
    WALLET_WITHDRAW = "wallet.withdraw"
    
    # Investment
    INVESTMENT_PURCHASE = "investment.purchase"
    INVESTMENT_CLAIM_INCOME = "investment.claim_income"
    
    # Support
    SUPPORT_TICKET_CREATE = "support.ticket_create"
    
    # Admin / Operational
    ADMIN_MANAGE_USERS = "admin.manage_users"
    ADMIN_MANAGE_FINANCE = "admin.manage_finance"
    ADMIN_SYSTEM_CONFIG = "admin.system_config"
    ADMIN_MAINTENANCE_TOGGLE = "admin.maintenance_toggle"


# Role-based hierarchy and permission mapping
# Maps each role to the set of PermissionScopes they possess
ROLE_PERMISSIONS: Final[Mapping[UserRole, set[PermissionScope]]] = {
    UserRole.GUEST: set(),
    UserRole.REGISTERED: {
        PermissionScope.WALLET_VIEW,
        PermissionScope.WALLET_DEPOSIT,
        PermissionScope.INVESTMENT_PURCHASE,
        PermissionScope.SUPPORT_TICKET_CREATE,
    },
    UserRole.VIP: {
        PermissionScope.WALLET_VIEW,
        PermissionScope.WALLET_DEPOSIT,
        PermissionScope.WALLET_WITHDRAW,
        PermissionScope.INVESTMENT_PURCHASE,
        PermissionScope.INVESTMENT_CLAIM_INCOME,
        PermissionScope.SUPPORT_TICKET_CREATE,
    },
    UserRole.ADMIN: {
        PermissionScope.WALLET_VIEW,
        PermissionScope.ADMIN_MANAGE_USERS,
        PermissionScope.ADMIN_MANAGE_FINANCE,
    },
    UserRole.SUPER_ADMIN: {scope for scope in PermissionScope},
}


def get_permissions_for_role(role: UserRole) -> set[PermissionScope]:
    """Retrieves the authoritative permission set for a given user role."""
    return ROLE_PERMISSIONS.get(role, set())


def is_authorized(role: UserRole, required_scope: PermissionScope) -> bool:
    """Evaluates if a specific role includes the required permission scope."""
    return required_scope in get_permissions_for_role(role)
