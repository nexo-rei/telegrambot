# __init__.py
"""Database Repositories Registry Initialization.

Exposes, structures, and simplifies interface boundaries for the data access layer
by aggregating and exporting the core generic base abstraction alongside explicit,
index-aware domain entities. Facilitates dependency injection workflows across services.
"""

from database.repositories.base_repo import BaseRepository
from database.repositories.user_repo import UserRepository
from database.repositories.financial_repo import FinancialRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "FinancialRepository",
]
