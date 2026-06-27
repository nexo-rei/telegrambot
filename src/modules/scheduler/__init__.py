# __init__.py
"""Scheduler Module Registry.

Aggregates and exposes the public interfaces for the platform's asynchronous 
task orchestration and background job management subsystem. This module 
handles the scheduling of recurring financial payouts, automated notifications, 
and system maintenance tasks within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public scheduler components
from src.modules.scheduler.handlers import SchedulerHandlers
from src.modules.scheduler.services import SchedulerService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "SchedulerHandlers",
    "SchedulerService",
]

