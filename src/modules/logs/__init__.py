# __init__.py
"""Logs Module Registry.

Aggregates and exposes the public interfaces for the platform's centralized 
event tracking, operational telemetry, and audit logging subsystem. This module 
provides the infrastructure for capturing, persisting, and querying system 
diagnostic data within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public logs components
from src.modules.logs.handlers import LogHandlers
from src.modules.logs.services import LogService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "LogHandlers",
    "LogService",
]
