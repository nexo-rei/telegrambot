# __init__.py
"""Investment Plans Module Registry.

Aggregates and exposes the public interfaces for the platform's investment 
products subsystem. This module manages the lifecycle of investment plans, 
including plan definitions, yield configurations, duration settings, and 
eligibility criteria for the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public investment plan components
from src.modules.investment_plans.handlers import InvestmentPlanHandlers
from src.modules.investment_plans.services import InvestmentPlanService
from src.modules.investment_plans.keyboards import InvestmentPlanKeyboards
from src.modules.investment_plans.dtos import InvestmentPlanDTOs

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "InvestmentPlanHandlers",
    "InvestmentPlanService",
    "InvestmentPlanKeyboards",
    "InvestmentPlanDTOs",
]
