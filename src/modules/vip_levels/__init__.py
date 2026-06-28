# __init__.py
"""

BUG FIX: All *Handlers class imports removed. Every handlers.py in the project
exports only a module-level `router` variable (aiogram Router), not a class.
Importing a non-existent class caused ImportError on every startup.
Fixed: import `router` directly; remove all non-existent class references.
"""

from typing import Final

__version__: Final[str] = "2.0.0"

from src.modules.vip_levels.handlers import router
from src.modules.vip_levels.services import VIPLevelService
from src.modules.vip_levels.keyboards import VIPLevelKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "router",
    "VIPLevelService",
    "VIPLevelKeyboards",
]
