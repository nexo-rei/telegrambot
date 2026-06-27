# services.py
"""Production-grade Daily Income Service.

Encapsulates business logic for the automated calculation, validation, and 
distribution of daily investment returns. Orchestrates atomic wallet 
transactions and financial reconciliation, ensuring high-precision yields 
across the investment portfolio.
"""

import logging
from typing import Final, Any
from decimal import Decimal
from datetime import datetime

from src.modules.daily_income.dtos import EarningsSummaryDTO, ClaimResultDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.daily_income.services")


class DailyIncomeService:
    """Core domain service for daily ROI management and claim orchestration."""

    def __init__(
        self,
        income_repo: Any,
        wallet_service: Any,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._income_repo: Final = income_repo
        self._wallet_service: Final = wallet_service
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_user_earnings_summary(self, user_id: int) -> EarningsSummaryDTO:
        """Aggregates and retrieves a user's current income status."""
        cache_key = f"earnings_summary_{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        # Logic to fetch accumulated but unclaimed daily returns
        pending = await self._income_repo.get_pending_amount(user_id)
        lifetime = await self._income_repo.get_lifetime_total(user_id)
        
        summary = EarningsSummaryDTO(
            daily_amount=pending,
            total_claimable=pending,
            lifetime_total=lifetime,
            is_claimable=pending > Decimal("0")
        )
        
        await self._cache.set(cache_key, summary, ttl=60)
        return summary

    async def process_daily_claim(self, user_id: int) -> ClaimResultDTO:
        """Orchestrates atomic claim of daily income and updates ledger."""
        
        # 1. Validation Logic
        pending_amount = await self._income_repo.get_pending_amount(user_id)
        if pending_amount <= Decimal("0"):
            return ClaimResultDTO(success=False, message="No income available to claim.")

        # 2. Atomic Financial Transaction
        try:
            async with self._transaction_repo.transaction():
                # Credit wallet and record in ledger
                await self._wallet_service.update_balance(
                    user_id, pending_amount, "daily_income_claim"
                )
                await self._income_repo.mark_as_claimed(user_id, pending_amount)
                
            await self._event_bus.publish("daily_income.claimed", {
                "user_id": user_id, 
                "amount": pending_amount
            })
            
            # Invalidate cache for summary
            await self._cache.delete(f"earnings_summary_{user_id}")
            
            return ClaimResultDTO(success=True, amount=pending_amount)

        except Exception as e:
            logger.error(f"Failed to process claim for {user_id}: {e}")
            return ClaimResultDTO(success=False, message="Claim processing failed.")
