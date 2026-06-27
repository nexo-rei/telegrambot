# __init__.py
"""Shared Middleware Subsystem Registry.

Aggregates and exposes the public middleware interfaces utilized for cross-cutting 
concerns, including anti-spam filtering, authentication enforcement, maintenance 
mode gating, and distributed rate limiting. Encapsulates implementation modules 
to ensure a clean, performant, and type-safe infrastructure layer.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public middleware handles to simplify consumer import paths
from src.shared.middleware.anti_spam import AntiSpamMiddleware
from src.shared.middleware.authentication import AuthenticationMiddleware
from src.shared.middleware.maintenance import MaintenanceMiddleware
from src.shared.middleware.rate_limiter import RateLimiterMiddleware

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AntiSpamMiddleware",
    "AuthenticationMiddleware",
    "MaintenanceMiddleware",
    "RateLimiterMiddleware",
]
