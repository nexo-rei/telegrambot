# __init__.py
"""

BUG FIX: All *Handlers class imports removed. Every handlers.py in the project
exports only a module-level `router` variable (aiogram Router), not a class.
Importing a non-existent class caused ImportError on every startup.
Fixed: import `router` directly; remove all non-existent class references.
"""

from typing import Final

__version__: Final[str] = "2.0.0"

from src.modules.fraud_security.handlers import router
from src.modules.fraud_security.services import FraudSecurityService

__all__: Final[list[str]] = [
    "__version__",
    "router",
    "FraudSecurityService",
]
