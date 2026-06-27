# __init__.py
"""Backup System Module Registry.

Aggregates and exposes the public interfaces for the platform's disaster 
recovery, data persistence, and integrity archiving subsystem. This module 
provides the foundational capabilities for automated database snapshots, 
state serialization, and secure off-site data preservation within the 
Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public backup system components
from src.modules.backup_system.handlers import BackupHandlers
from src.modules.backup_system.services import BackupService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "BackupHandlers",
    "BackupService",
]
