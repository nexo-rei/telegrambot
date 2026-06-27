# __init__.py
"""Shared Caching Subsystem Configuration Registry.

Aggregates and exposes the public operational boundaries of the infrastructure
caching layer. Provides decoupled wrappers for distributed lock execution grids
and asynchronous client pooling adapters while keeping internal driver parameters
isolated from core application domain tasks.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly export public abstraction handles
from src.shared.cache.redis_client import RedisCacheClient
from src.shared.cache.lock_manager import DistributedLockManager

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__license__",
    "RedisCacheClient",
    "DistributedLockManager",
]
