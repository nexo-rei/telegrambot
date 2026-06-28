# __init__.py
"""Database Enums Package Registry.

Aggregates and exposes the canonical enumeration types for the platform's 
PostgreSQL data layer.

BUG FIX: The original __init__.py exported `VerificationLevel` which does not exist
in account_roles.py. The actual class is named `VerificationStatus`. Fixed export name.
"""

from typing import Final

# Package Metadata
__version__: Final[str] = "1.0.0"

# BUG FIX: Exported VerificationLevel -> does not exist. Class is VerificationStatus.
from database.enums.financial_states import (
    TransactionStatus,
    InvestmentStatus,
    WithdrawalStatus,
)
from database.enums.account_roles import (
    UserRole,
    AccountStatus,
    VerificationStatus,  # Fixed: was incorrectly exported as VerificationLevel
)

__all__: Final[list[str]] = [
    "__version__",
    "TransactionStatus",
    "InvestmentStatus",
    "WithdrawalStatus",
    "UserRole",
    "AccountStatus",
    "VerificationStatus",
]
