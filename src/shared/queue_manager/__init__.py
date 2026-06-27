# __init__.py
"""Shared Asynchronous Task Queue Management Subsystem Registry.

Aggregates and exposes the public interfaces for managing distributed background 
task processing. Encapsulates the Celery broker configuration and task dispatching 
logic to ensure a decoupled, performant, and reliable mechanism for handling 
asynchronous operations like notifications, financial processing, and system reports.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public queue management components
from src.shared.queue_manager.celery_broker import CeleryBroker, celery_app

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "CeleryBroker",
    "celery_app",
]
