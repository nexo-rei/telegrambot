# __init__.py
"""Transactions Module Registry.

Aggregates and exposes the public interfaces for the platform's transaction 
subsystem. This module serves as the central ledger for all financial movements, 
providing audit trails for deposits, withdrawals, and investment-related 
activity within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public transaction components
from src.modules.transactions.handlers import TransactionHandlers
from src.modules.transactions.services import TransactionService
from src.modules.transactions.keyboards import TransactionKeyboards
from src.modules.transactions.dtos import TransactionDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "TransactionHandlers",
    "TransactionService",
    "TransactionKeyboards",
    "TransactionDTOs",
]

