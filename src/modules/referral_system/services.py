# services.py
"""Production-grade Referral System Service.

Encapsulates business logic for user referral tracking, commission structures, 
and reward distribution. Manages the referral hierarchy and maintains atomic 
financial records for affiliate performance, ensuring data integrity across 
the platform's ledger.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.referral_system.dtos import ReferralStatsDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.referral_system.services")


class ReferralService:
    """Core domain service for affiliate network management and reward attribution."""

    def __init__(
        self,
        referral_repo: Any,
        wallet_service: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._referral_repo: Final = referral_repo
        self._wallet_service: Final = wallet_service
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_user_stats(self, user_id: int) -> ReferralStatsDTO:
        """Retrieves cached referral performance statistics for a user."""
        cache_key = f"ref_stats_{user_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        stats = await self._referral_repo.get_stats(user_id)
        await self._cache.set(cache_key, stats, ttl=600)
        return stats

    async def register_referral(self, referrer_id: int, referee_id: int) -> bool:
        """Registers a new user within the referral hierarchy."""
        if referrer_id == referee_id:
            logger.warning(f"Self-referral attempt by {user_id}")
            return False

        success = await self._referral_repo.create_link(referrer_id, referee_id)
        if success:
            await self._event_bus.publish("referral.registered", {
                "referrer_id": referrer_id, 
                "referee_id": referee_id
            })
            await self._cache.delete(f"ref_stats_{referrer_id}")
        return success

    async def distribute_reward(self, referrer_id: int, amount: Decimal) -> bool:
        """Calculates and applies referral commissions atomically."""
        try:
            # Commission calculation logic
            commission = PrecisionMath.multiply(amount, Decimal("0.05"))
            
            async with self._referral_repo.transaction():
                await self._wallet_service.update_balance(
                    referrer_id, commission, "referral_reward"
                )
                await self._referral_repo.record_reward(referrer_id, commission)
                
            await self._event_bus.publish("referral.reward_distributed", {
                "referrer_id": referrer_id, 
                "amount": commission
            })
            return True
        except Exception as e:
            logger.error(f"Failed to distribute referral reward: {e}")
            return False
