# __init__.py
"""Shared Middleware Subsystem Registry.

BUG FIX: The original __init__.py imported from `src.shared.middleware` (correct spelling)
but the actual package directory on disk is `src/shared/middlware` (typo: missing 'd').
Fixed all import paths to match the actual directory name `middlware`.
"""

from typing import Final

__version__: Final[str] = "2.0.0"

# BUG FIX: Changed `src.shared.middleware` -> `src.shared.middlware` to match actual directory
from src.shared.middlware.anti_spam import AntiSpamMiddleware
from src.shared.middlware.authentication import AuthenticationMiddleware
from src.shared.middlware.maintenance import MaintenanceMiddleware
from src.shared.middlware.rate_limiter import RateLimiterMiddleware

__all__: Final[list[str]] = [
    "__version__",
    "AntiSpamMiddleware",
    "AuthenticationMiddleware",
    "MaintenanceMiddleware",
    "RateLimiterMiddleware",
]
