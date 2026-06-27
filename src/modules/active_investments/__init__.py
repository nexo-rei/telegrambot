# __init__.py
"""Active Investments Module Registry.

Aggregates and exposes the public interfaces for the platform's active 
investment portfolio subsystem. This module manages real-time monitoring of 
user investments, tracking ROI accumulation, maturity status, and lifecycle 
management for all currently active financial positions within the Nigerian 
Investment Platform ecosystem.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public active investment components
from src.modules.active_investments.handlers import ActiveInvestmentHandlers
from src.modules.active_investments.services import ActiveInvestmentService
from src.modules.active_investments.dtos import ActiveInvestmentDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "ActiveInvestmentHandlers",
    "ActiveInvestmentService",
    "ActiveInvestmentDTOs",
]
