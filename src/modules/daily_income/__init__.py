# __init__.py
"""Daily Income Module Registry.

Aggregates and exposes the public interfaces for the platform's daily 
yield distribution subsystem. This module orchestrates the automated 
calculation and allocation of daily investment returns, ensuring consistent 
financial growth for users within the Nigerian Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public daily income components
from src.modules.daily_income.handlers import DailyIncomeHandlers
from src.modules.daily_income.services import DailyIncomeService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "DailyIncomeHandlers",
    "DailyIncomeService",
]
