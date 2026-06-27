# __init__.py
"""Media Manager Module Registry.

Aggregates and exposes the public interfaces for the platform's multimedia 
processing, transcoding, and content delivery subsystem. This module provides 
the high-level abstractions for handling image manipulation, video transcoding 
via FFmpeg, and optimized media serving within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public media manager components
from src.modules.media_manager.handlers import MediaManagerHandlers
from src.modules.media_manager.services import MediaManagerService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "MediaManagerHandlers",
    "MediaManagerService",
]
