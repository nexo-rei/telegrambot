# __init__.py
"""Shared Foundational Filters Package Central Registry.

Aggregates and exposes the public filter interfaces used by Aiogram handlers to govern
request authorization, account state validation, and operational status checks. 
Provides decoupled, reusable filter primitives to maintain clean, readable, and 
type-safe message/callback routing logic.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly export public filter classes for usage in handler routers
from src.shared.filters.is_admin import IsAdmin
from src.shared.filters.is_registered import IsRegistered
from src.shared.filters.payment_status import PaymentStatusFilter

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "IsAdmin",
    "IsRegistered",
    "PaymentStatusFilter",
]
