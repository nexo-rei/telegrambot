# __init__.py
"""Referral System Module Registry.

Aggregates and exposes the public interfaces for the platform's referral and 
affiliate marketing subsystem. This module manages invite code generation, 
network tree traversal, bonus attribution, and commission structures for the 
Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public referral components
from src.modules.referral_system.handlers import ReferralHandlers
from src.modules.referral_system.services import ReferralService
from src.modules.referral_system.keyboards import ReferralKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "ReferralHandlers",
    "ReferralService",
    "ReferralKeyboards",
]

