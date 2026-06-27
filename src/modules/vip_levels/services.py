# services.py
"""Production-grade VIP Level Service.

Encapsulates business logic for the VIP tier progression lifecycle, 
benefit activation, and secure upgrade processing. Orchestrates atomic 
financial transactions between the user's wallet and platform loyalty 
tiers, ensuring high-precision benefit scaling and reconciliation.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.vip_levels.dtos import VIPStatusDTO, UpgradeResultDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.vip_levels.services")


class VIPLevelService:
    """Core domain service for VIP level management and benefit orchestration."""

    def __init__(
        self,
        vip_repo: Any,
        wallet_service: Any,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._vip_repo: Final = vip_repo
        self._wallet_service: Final = wallet_service
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_user_vip_status(self, user_id: int) -> VIPStatusDTO:
        """Retrieves cached VIP profile and tier progression metrics."""
        cache_key = f"vip_status_{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        status = await self._vip_repo.get_user_status(user_id)
        await self._cache.set(cache_key, status, ttl=600)
        return status

    async def process_upgrade(self, user_id: int) -> UpgradeResultDTO:
        """Orchestrates the atomic purchase and promotion of a user's VIP tier."""
        
        # 1. Eligibility and Balance Validation
        status = await self.get_user_vip_status(user_id)
        if not status.can_upgrade:
            return UpgradeResultDTO(success=False, message="Upgrade not eligible.")

        # 2. Atomic Financial Transaction
        try:
            async with self._transaction_repo.transaction():
                # Deduct cost from wallet
                await self._wallet_service.debit_balance(
                    user_id, status.upgrade_cost, "vip_upgrade_purchase"
                )
                # Promote level in database
                new_level = await self._vip_repo.promote_user(user_id)
            
            # Notify domain modules
            await self._event_bus.publish("vip.upgraded", {
                "user_id": user_id, 
                "new_level": new_level
            })
            
            # Invalidate cache
            await self._cache.delete(f"vip_status_{user_id}")
            
            return UpgradeResultDTO(
                success=True, 
                new_level=new_level, 
                message="Upgrade successful."
            )

        except Exception as e:
            logger.error(f"VIP upgrade transaction failed for {user_id}: {e}")
            return UpgradeResultDTO(success=False, message="Upgrade transaction failed.")
          
