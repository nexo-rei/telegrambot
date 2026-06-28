# __init__.py
"""

BUG FIX: All *Handlers class imports removed. Every handlers.py in the project
exports only a module-level `router` variable (aiogram Router), not a class.
Importing a non-existent class caused ImportError on every startup.
Fixed: import `router` directly; remove all non-existent class references.
"""

from typing import Final

__version__: Final[str] = "2.0.0"

from src.modules.wallet.handlers import router
from src.modules.wallet.services import WalletService
from src.modules.wallet.keyboards import WalletKeyboards
from src.modules.wallet.states import WalletStates

__all__: Final[list[str]] = [
    "__version__",
    "router",
    "WalletService",
    "WalletKeyboards",
    "WalletStates",
]
