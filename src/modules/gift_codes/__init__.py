# __init__.py
"""Gift Codes Module Registry.

Aggregates and exposes the public interfaces for the platform's promotional 
gift code distribution and redemption subsystem. This module orchestrates 
the secure validation, activation, and financial crediting of bonus incentives 
offered to users within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public gift code components
from src.modules.gift_codes.handlers import GiftCodeHandlers
from src.modules.gift_codes.services import GiftCodeService
from src.modules.gift_codes.keyboards import GiftCodeKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "GiftCodeHandlers",
    "GiftCodeService",
    "GiftCodeKeyboards",
]
