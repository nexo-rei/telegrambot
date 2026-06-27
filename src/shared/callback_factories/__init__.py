# __init__.py
"""Shared Callback Data Factories Package Central Registry.

Aggregates, coordinates, and exposes strongly-typed CallbackData factories 
leveraged by the presentation layer for secure, deterministic inline keyboard routing. 
Encapsulates low-level string formatting and binary state serializations within cohesive 
infrastructure blocks.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public typed callback factories to decouple consumers from implementation structures
from src.shared.callback_factories.navigation import NavigationCallback
from src.shared.callback_factories.investment import InvestmentCallback
from src.shared.callback_factories.admin import AdminCallback

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__license__",
    "NavigationCallback",
    "InvestmentCallback",
    "AdminCallback",
]

