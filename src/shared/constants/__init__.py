# __init__.py
"""Shared Application Constants Package Central Registry.

Aggregates, coordinates, and exposes global domain invariants, system-wide configuration
thresholds, business metrics parameters, and operational bounds. Ensures strict data 
consistency across service calculations, data layers, and the user interface.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public constants modules to expose high-level variables cleanly
from src.shared.constants.financial import *
from src.shared.constants.system import *

# Define the comprehensive runtime export manifest dynamically/explicitly for consumers
__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__license__",
    
    # Financial Invariants Matrix Exports
    "MIN_DEPOSIT_AMOUNT_NGN",
    "MAX_DEPOSIT_AMOUNT_NGN",
    "MIN_WITHDRAWAL_AMOUNT_NGN",
    "MAX_WITHDRAWAL_AMOUNT_NGN",
    "DEFAULT_CURRENCY_SYMBOL",
    "DEFAULT_CURRENCY_CODE",
    "WITHDRAWAL_FEE_PERCENTAGE",
    
    # System Operational Boundary Matrix Exports
    "PLATFORM_TIMEZONE",
    "MAX_PAGE_SIZE_LIMIT",
    "USER_SESSION_TTL_SECONDS",
    "DEFAULT_DATE_FORMAT",
    "SUPPORTED_LANGUAGES",
]
