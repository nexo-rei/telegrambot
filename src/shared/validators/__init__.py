# __init__.py
"""Shared Input Validation and Business Rules Subsystem Registry.

Aggregates and exposes the public interfaces for validating financial transactions,
user-provided data, and platform business constraints. Encapsulates validation
logic to ensure that only sanitized and verified data reaches the core services,
thereby maintaining system integrity and security.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public validation management components
from src.shared.validators.financial_validator import (
    FinancialValidator,
    ValidationError,
    ValidationResult,
)

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "FinancialValidator",
    "ValidationError",
    "ValidationResult",
]
