# __init__.py
"""VIP Levels Module Registry.

Aggregates and exposes the public interfaces for the platform's VIP and 
loyalty tier management subsystem. This module orchestrates user progression 
through various investment levels, eligibility validation for premium benefits, 
and automated tier-based reward scaling within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public VIP level components
from src.modules.vip_levels.handlers import VIPLevelHandlers
from src.modules.vip_levels.services import VIPLevelService
from src.modules.vip_levels.keyboards import VIPLevelKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "VIPLevelHandlers",
    "VIPLevelService",
    "VIPLevelKeyboards",
]

