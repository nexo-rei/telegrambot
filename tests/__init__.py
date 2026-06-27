# __init__.py
"""Automated Testing Package.

This package acts as the root namespace for the platform's test suite, 
integrating unit, integration, and end-to-end testing modules. It facilitates 
discovery by pytest and provides shared configuration, fixtures, and 
utilities to ensure platform reliability and code quality.
"""

from typing import Final

# Package Metadata
__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"

# Expose shared testing utilities or global fixtures if required
# in future iterations. Keeping this clean for discovery.

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
]
