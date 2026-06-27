# __init__.py
"""Dashboard Module Registry.

Aggregates and exposes the public interfaces for the platform's central 
dashboard subsystem. This module manages the primary user interface for 
investment monitoring, account summaries, and navigation to core financial 
features, ensuring a streamlined and premium experience within the 
Telegram ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public dashboard components
from src.modules.dashboard.handlers import DashboardHandlers
from src.modules.dashboard.services import DashboardService
from src.modules.dashboard.keyboards import DashboardKeyboards
from src.modules.dashboard.states import DashboardStates
from src.modules.dashboard.dtos import DashboardDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "DashboardService",
    "DashboardHandlers",
    "DashboardKeyboards",
    "DashboardStates",
    "DashboardDTOs",
]
