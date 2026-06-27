# __init__.py
"""Wallet Module Registry.

Aggregates and exposes the public interfaces for the platform's financial 
wallet subsystem. This module manages user balance, deposit/withdrawal 
workflows, and transactional integrity, ensuring secure and accurate 
tracking of funds within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public wallet components
from src.modules.wallet.handlers import WalletHandlers
from src.modules.wallet.services import WalletService
from src.modules.wallet.keyboards import WalletKeyboards
from src.modules.wallet.states import WalletStates
from src.modules.wallet.dtos import WalletDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "WalletHandlers",
    "WalletService",
    "WalletKeyboards",
    "WalletStates",
    "WalletDTOs",
]

