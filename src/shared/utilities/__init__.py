# __init__.py
"""Shared Utilities and Helper Subsystem Registry.

Aggregates and exposes the public interfaces for low-level platform utility 
modules. Encapsulates reusable logic for cryptographic operations, financial 
precision math, and general-purpose helpers, ensuring a standardized and 
efficient codebase across all application layers.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public utility components
from src.shared.utilities.crypto_cipher import CryptoCipher
from src.shared.utilities.math_precision import PrecisionMath

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "CryptoCipher",
    "PrecisionMath",
]
