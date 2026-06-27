# __init__.py
"""File Storage Module Registry.

Aggregates and exposes the public interfaces for the platform's distributed 
file management and object storage abstraction subsystem. This module provides 
the infrastructure for secure uploading, processing, retrieval, and lifecycle 
management of media and document assets within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public file storage components
from src.modules.file_storage.handlers import FileStorageHandlers
from src.modules.file_storage.services import FileStorageService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "FileStorageHandlers",
    "FileStorageService",
]
