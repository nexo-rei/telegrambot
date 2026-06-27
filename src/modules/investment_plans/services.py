# services.py
"""Production-grade Investment Plan Service.

Encapsulates all business logic for investment products, including yield 
calculations, eligibility validation, and atomic purchasing orchestration. 
Ensures high-precision financial operations using Decimal arithmetic and 
maintains state consistency across the wallet and investment repositories.
"""

import logging
from typing import Final, Any, List
from decimal import Decimal

from src.modules.investment_plans.dtos import InvestmentPlanDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.investment_plans.services")


class InvestmentPlanService:
    """Core domain service for managing investment lifecycle and ROI projections."""

    def __init__(
        self,
        plan_repo: Any,
        wallet_service: Any,
        investment_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._plan_repo: Final = plan_repo
        self._wallet_service: Final = wallet_service
        self._investment_repo: Final = investment_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_all_active_plans(self) -> List[InvestmentPlanDTO]:
        """Retrieves and caches available investment plans."""
        cache_key = "active_investment_plans"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        plans = await self._plan_repo.get_active_plans()
        await self._cache.set(cache_key, plans, ttl=3600)
        return plans

    async def calculate_roi(self, amount: Decimal, plan: InvestmentPlanDTO) -> Decimal:
        """Calculates total projected return for a given investment amount."""
        roi_multiplier = plan.roi_percentage / Decimal("100")
        return PrecisionMath.multiply(amount, roi_multiplier)

    async def validate_purchase_eligibility(self, user_id: int, plan_id: str) -> bool:
        """Validates if a user meets requirements to purchase the specified plan."""
        plan = await self._plan_repo.get_by_id(plan_id)
        if not plan or not plan.is_active:
            return False
            
        summary = await self._wallet_service.get_wallet_summary(user_id)
        if summary.available_balance < plan.min_amount:
            return False
            
        return True

    async def purchase_plan(self, user_id: int, plan_id: str, amount: Decimal) -> str:
        """Orchestrates atomic investment purchase and wallet debit."""
        plan = await self._plan_repo.get_by_id(plan_id)
        
        if amount < plan.min_amount or amount > plan.max_amount:
            raise ValueError("Investment amount outside plan boundaries.")

        # Atomic transaction: Debit wallet and create investment
        async with self._investment_repo.transaction():
            await self._wallet_service.update_balance(
                user_id, -amount, "investment_purchase"
            )
            investment_id = await self._investment_repo.create_active(
                user_id=user_id,
                plan_id=plan_id,
                amount=amount,
                expected_roi=await self.calculate_roi(amount, plan)
            )

        await self._event_bus.publish("investment.purchased", {"user_id": user_id, "plan_id": plan_id})
        logger.info(f"User {user_id} successfully purchased plan {plan_id}")
        
        return investment_id
