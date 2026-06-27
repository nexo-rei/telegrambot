# services.py
"""Production-grade Referral Reward Service.

Encapsulates business logic for the calculation, validation, and atomic 
distribution of referral-based financial incentives. Manages the lifecycle 
of affiliate commissions, ensuring accurate reconciliation between the 
referral network and the user's primary wallet.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.referral_rewards.dtos import RewardSummaryDTO, ClaimResultDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.referral_rewards.services")


class ReferralRewardService:
    """Core domain service for managing affiliate reward lifecycles and claims."""

    def __init__(
        self,
        reward_repo: Any,
        wallet_service: Any,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._reward_repo: Final = reward_repo
        self._wallet_service: Final = wallet_service
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_reward_summary(self, user_id: int) -> RewardSummaryDTO:
        """Retrieves aggregated reward performance for a user."""
        cache_key = f"reward_summary_{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        pending = await self._reward_repo.get_pending_total(user_id)
        lifetime = await self._reward_repo.get_lifetime_total(user_id)
        
        summary = RewardSummaryDTO(
            pending_amount=pending,
            lifetime_amount=lifetime,
            has_pending=pending > Decimal("0")
        )
        
        await self._cache.set(cache_key, summary, ttl=300)
        return summary

    async def process_reward_claim(self, user_id: int) -> ClaimResultDTO:
        """Orchestrates the atomic claim process for referral commissions."""
        
        pending_amount = await self._reward_repo.get_pending_total(user_id)
        if pending_amount <= Decimal("0"):
            return ClaimResultDTO(success=False, message="No claimable rewards found.")

        try:
            # Atomic transaction to ensure ledger consistency
            async with self._transaction_repo.transaction():
                # Credit wallet via wallet service
                await self._wallet_service.update_balance(
                    user_id, pending_amount, "referral_reward_claim"
                )
                # Update reward record state
                await self._reward_repo.mark_as_claimed(user_id)
            
            # Publish event for analytics and downstream modules
            await self._event_bus.publish("referral_reward.claimed", {
                "user_id": user_id, 
                "amount": pending_amount
            })
            
            # Clear cache to force data refresh
            await self._cache.delete(f"reward_summary_{user_id}")
            
            return ClaimResultDTO(success=True, amount=pending_amount)

        except Exception as e:
            logger.error(f"Atomic reward claim failed for {user_id}: {e}")
            return ClaimResultDTO(success=False, message="Financial reconciliation error.")
