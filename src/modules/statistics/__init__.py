# __init__.py
"""Statistics Module Registry.

Aggregates and exposes the public interfaces for the platform's analytical 
and metrics-tracking subsystem. This module processes high-volume data points 
to provide real-time insights into user activity, financial health, and 
investment performance within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public statistics components
from src.modules.statistics.handlers import StatisticsHandlers
from src.modules.statistics.services import StatisticsService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "StatisticsHandlers",
    "StatisticsService",
]

