# __init__.py
"""Shared Role-Based Access Control (RBAC) Subsystem Registry.

Aggregates and exposes the public interfaces for managing fine-grained platform
permissions. Encapsulates authorization logic, scope-based access definitions,
and guard clauses to ensure consistent security posture across all financial,
administrative, and operational modules.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public permission management components
from src.shared.permissions.guard import PermissionGuard
from src.shared.permissions.scopes import PermissionScope, PermissionLevel

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "PermissionGuard",
    "PermissionScope",
    "PermissionLevel",
]
