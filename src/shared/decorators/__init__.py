# __init__.py
"""Shared Decorator Subsystem Configuration Registry.

Aggregates and exposes the public decorator interfaces utilized for cross-cutting 
aspects such as rate limiting, transactional integrity, and role-based access control.
Encapsulates implementation modules to ensure a clean, performant API surface area.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public decorator handles to simplify consumer import paths
from src.shared.decorators.rate_limit import rate_limit
from src.shared.decorators.transactional import transactional
from src.shared.decorators.role_required import role_required

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__license__",
    "rate_limit",
    "transactional",
    "role_required",
]
