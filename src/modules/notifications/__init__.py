# __init__.py
"""Notifications Module Registry.

Aggregates and exposes the public interfaces for the platform's multi-channel 
notification subsystem. This module orchestrates the dispatch of alerts, 
investment updates, and system communications to users, ensuring reliable 
delivery across the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public notification components
from src.modules.notifications.handlers import NotificationHandlers
from src.modules.notifications.services import NotificationService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "NotificationHandlers",
    "NotificationService",
]
