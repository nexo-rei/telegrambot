# __init__.py
"""Deposits Module Registry.

Aggregates and exposes the public interfaces for the platform's deposit 
subsystem. This module manages user funding flows, payment gateway integration, 
and deposit reconciliation, ensuring secure and atomic processing of funds 
within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public deposit components
from src.modules.deposits.handlers import DepositHandlers
from src.modules.deposits.services import DepositService
from src.modules.deposits.keyboards import DepositKeyboards
from src.modules.deposits.states import DepositStates
from src.modules.deposits.dtos import DepositDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "DepositHandlers",
    "DepositService",
    "DepositKeyboards",
    "DepositStates",
    "DepositDTOs",
]
