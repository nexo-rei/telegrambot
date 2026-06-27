# __init__.py
"""Shared Payment Gateway Adapter Subsystem Registry.

Aggregates and exposes the public interfaces for integrating external financial
gateways. Provides a unified, polymorphic abstraction layer for processing
deposits, withdrawals, and transaction verification across heterogeneous payment
providers while maintaining clean, decoupled architectural boundaries.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public payment adapter interfaces to simplify consumer imports
from src.shared.payment_adapters.base_adapter import BasePaymentAdapter
from src.shared.payment_adapters.paystack_adapter import PaystackAdapter

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "BasePaymentAdapter",
    "PaystackAdapter",
]
