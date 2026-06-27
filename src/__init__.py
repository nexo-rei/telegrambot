# __init__.py
"""Enterprise Telegram Investment Bot.

An asynchronous, production-ready financial ecosystem built using a clean, 
decoupled architecture pattern. This package coordinates capital asset distribution 
channels, fixed-point monetary ledger allocations, automated downline multi-tier affiliate networks, 
and helpdesk ticketing vectors over Telegram securely.

Architecture: Clean / Domain-Driven Design (DDD)
Frameworks: Aiogram 3.x, SQLAlchemy 2.x Async, Celery 5.x, Redis, PostgreSQL
Python: 3.13+ Production Runtime Matrix
"""

from typing import Final

# System-Wide Platform Metadata Attributes
__title__: Final[str] = "Enterprise Telegram Investment Bot"
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Export package manifest elements explicitly
__all__: Final[list[str]] = [
    "__title__",
    "__version__",
    "__author__",
    "__license__",
]
