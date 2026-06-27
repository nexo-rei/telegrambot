# __init__.py
"""Announcements Module Registry.

Aggregates and exposes the public interfaces for the platform's global 
announcement and system-wide broadcast subsystem. This module manages 
the distribution of important platform updates, policy changes, and 
promotional news to all active users within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public announcement components
from src.modules.announcements.handlers import AnnouncementHandlers
from src.modules.announcements.services import AnnouncementService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AnnouncementHandlers",
    "AnnouncementService",
]
