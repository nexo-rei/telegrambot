# __init__.py
"""Database Enums Package Registry.

Aggregates and exposes the canonical enumeration types for the platform's 
PostgreSQL data layer. This package serves as the single point of truth for 
all database-mapped state machines, role definitions, and categorical 
constants utilized by SQLAlchemy models within the Nigerian Investment Platform.
"""

from typing import Final

# Package Metadata
__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Exported Enumerations
from database.enums.financial_states import (
    TransactionStatus, 
    InvestmentStatus, 
    WithdrawalStatus
)
from database.enums.account_roles import (
    UserRole, 
    AccountStatus, 
    VerificationLevel
)

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "TransactionStatus",
    "InvestmentStatus",
    "WithdrawalStatus",
    "UserRole",
    "AccountStatus",
    "VerificationLevel",
]
