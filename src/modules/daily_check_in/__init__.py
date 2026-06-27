# __init__.py
"""Daily Check-In Module Registry.

Aggregates and exposes the public interfaces for the platform's daily user 
engagement and rewards subsystem. This module orchestrates the tracking of 
consecutive check-ins, validation of eligibility, and allocation of loyalty 
bonuses within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public daily check-in components
from src.modules.daily_check_in.handlers import DailyCheckInHandlers
from src.modules.daily_check_in.services import DailyCheckInService
from src.modules.daily_check_in.keyboards import DailyCheckInKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "DailyCheckInHandlers",
    "DailyCheckInService",
    "DailyCheckInKeyboards",
]
