# __init__.py
"""Moderators Module Registry.

Aggregates and exposes the public interfaces for the platform's moderation 
and compliance subsystem. This module orchestrates administrative oversight 
of user interactions, dispute resolution, and content monitoring to ensure 
platform integrity within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public moderator components
from src.modules.moderators.handlers import ModeratorHandlers
from src.modules.moderators.services import ModeratorService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "ModeratorHandlers",
    "ModeratorService",
]
