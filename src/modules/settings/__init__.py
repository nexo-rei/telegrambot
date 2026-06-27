# __init__.py
"""Settings Module Registry.

Aggregates and exposes the public interfaces for the platform's dynamic 
configuration and user-preference management subsystem. This module provides 
the infrastructure for maintaining application-wide parameters, user-specific 
customizations, and feature-flag persistence within the Nigerian Investment 
Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public settings components
from src.modules.settings.handlers import SettingsHandlers
from src.modules.settings.services import SettingsService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "SettingsHandlers",
    "SettingsService",
]

