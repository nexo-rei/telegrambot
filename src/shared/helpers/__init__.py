# __init__.py
"""Shared Foundational Utilities Package Registry.

Aggregates and exposes the public helper interfaces utilized for cross-cutting 
tasks including currency localization, financial formatting, and IANA-compliant 
chronological calculations. Encapsulates utility implementations to ensure a 
clean, performant, and type-safe API surface area for the entire application.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public helper interfaces to simplify consumer import paths
from src.shared.helpers.currency_formatter import format_ngn_currency
from src.shared.helpers.datetime_utils import format_to_local_time, get_now_utc

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "format_ngn_currency",
    "format_to_local_time",
    "get_now_utc",
]
