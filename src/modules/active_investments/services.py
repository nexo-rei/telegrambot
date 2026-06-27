# services.py
"""Production-grade Active Investment Service.

Encapsulates business logic for monitoring active investment positions, tracking 
real-time yield accumulation, and managing the lifecycle of financial assets. 
Ensures high-precision financial tracking via Decimal arithmetic and provides 
performant access to investment portfolio data through a cache-first architecture.
"""

import logging
from typing import Final, Any, List
from decimal import Decimal
from datetime import datetime

from src.modules.active_investments.dtos import InvestmentDetailsDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.active_investments.services")


class ActiveInvestmentService:
    """Core domain service for tracking active investment progress and lifecycle states."""

    def __init__(
        self,
        investment_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._investment_repo: Final = investment_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_user_portfolio(self, user_id: int) -> List[Any]:
        """Retrieves the list of a user's active investment positions."""
        cache_key = f"portfolio_{user_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        portfolio = await self._investment_repo.get_active_by_user(user_id)
        await self._cache.set(cache_key, portfolio, ttl=300)
        return portfolio

    async def get_investment_details(self, investment_id: str) -> InvestmentDetailsDTO:
        """Calculates current ROI progress and maturity metrics for a position."""
        investment = await self._investment_repo.get_by_id(investment_id)
        if not investment:
            raise ValueError("Investment position not found.")

        # Financial Calculations
        now = datetime.now()
        age = (now - investment.created_at).days
        progress = PrecisionMath.divide(Decimal(age), Decimal(investment.duration_days))
        progress_pct = PrecisionMath.multiply(progress, Decimal("100"))

        daily_earnings = PrecisionMath.divide(investment.expected_roi, Decimal(investment.duration_days))
        
        return InvestmentDetailsDTO(
            investment_id=investment.id,
            amount=investment.amount,
            status=investment.status,
            progress_percentage=min(progress_pct, Decimal("100")),
            daily_earnings=daily_earnings
        )

    async def synchronize_lifecycle(self, investment_id: str) -> None:
        """Checks for maturity and updates investment state if necessary."""
        investment = await self._investment_repo.get_by_id(investment_id)
        
        if investment.status == "active" and self._is_matured(investment):
            await self._investment_repo.update_status(investment_id, "matured")
            await self._event_bus.publish("investment.matured", {"id": investment_id})
            logger.info(f"Investment {investment_id} reached maturity.")

    def _is_matured(self, investment: Any) -> bool:
        """Determines if the investment duration has elapsed."""
        return (datetime.now() - investment.created_at).days >= investment.duration_days
