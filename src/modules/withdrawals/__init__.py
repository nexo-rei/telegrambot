# __init__.py
"""Withdrawals Module Registry.

Aggregates and exposes the public interfaces for the platform's withdrawal 
subsystem. This module manages user fund outflow requests, bank account 
validation, approval workflows, and automated payout processing, ensuring 
secure and reliable financial distributions within the Nigerian Investment 
Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public withdrawal components
from src.modules.withdrawals.handlers import WithdrawalHandlers
from src.modules.withdrawals.services import WithdrawalService
from src.modules.withdrawals.keyboards import WithdrawalKeyboards
from src.modules.withdrawals.states import WithdrawalStates
from src.modules.withdrawals.dtos import WithdrawalDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "WithdrawalHandlers",
    "WithdrawalService",
    "WithdrawalKeyboards",
    "WithdrawalStates",
    "WithdrawalDTOs",
]

