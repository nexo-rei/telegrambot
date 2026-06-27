# __init__.py
"""Database Models Central Registry.

Aggregates, binds, and exposes all domain data models inheriting from the core
Declarative Base. Serves as the authoritative source of truth for the object-
relational mapping layer, ensuring comprehensive entity tracking for Alembic 
migration discoveries while preventing structural circular dependencies.
"""

from database.models.user import User
from database.models.wallet import Wallet
from database.models.investment import Investment
from database.models.transaction import Transaction
from database.models.referral import Referral
from database.models.ticket import Ticket
from database.models.core_logs import CoreLog

__all__ = [
    "User",
    "Wallet",
    "Investment",
    "Transaction",
    "Referral",
    "Ticket",
    "CoreLog",
]
