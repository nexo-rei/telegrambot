# __init__.py
"""Analytics Module Registry.

Aggregates and exposes the public interfaces for the platform's internal 
behavioral tracking and event analysis subsystem. This module provides the 
foundational tools for logging, processing, and analyzing user interaction 
patterns and system performance events within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public analytics components
from src.modules.analytics.handlers import AnalyticsHandlers
from src.modules.analytics.services import AnalyticsService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AnalyticsHandlers",
    "AnalyticsService",
]
