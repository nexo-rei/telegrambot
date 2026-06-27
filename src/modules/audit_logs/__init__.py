# __init__.py
"""Audit Logs Module Registry.

Aggregates and exposes the public interfaces for the platform's immutable 
compliance and security auditing subsystem. This module provides the 
mechanisms for recording, persisting, and verifying sensitive administrative 
and financial operations within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public audit logs components
from src.modules.audit_logs.handlers import AuditLogHandlers
from src.modules.audit_logs.services import AuditLogService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AuditLogHandlers",
    "AuditLogService",
]
