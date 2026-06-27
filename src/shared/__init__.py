# __init__.py
"""Shared Foundational Utilities Package Central Registry.

Aggregates and exports core platform primitives, cross-cutting middleware components,
validation engines, custom filters, and security permissions. Acts as a decoupled,
low-overhead integration interface shared across the domain core, service layers, 
and application entry blocks.
"""

from typing import Final

# System-Wide Foundational Package Metadata
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Package Public Namespace Interface Definition Manifest
__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    
    # Structural module bindings will be lazily or explicitly mapped 
    # during active consumer runtime linking to optimize package memory.
]
