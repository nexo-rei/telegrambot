# __init__.py
"""Cron Jobs Module Registry.

Aggregates and exposes the public interfaces for the platform's time-triggered 
task registry and execution management subsystem. This module provides the 
declarative infrastructure for defining, validating, and managing recurring 
background operations within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public cron jobs components
from src.modules.cron_jobs.handlers import CronJobHandlers
from src.modules.cron_jobs.services import CronJobService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "CronJobHandlers",
    "CronJobService",
]
