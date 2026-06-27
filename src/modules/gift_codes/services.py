# services.py
"""Production-grade Gift Code Service.

Encapsulates business logic for promotional campaign management, secure 
redemption validation, and atomic reward distribution. Orchestrates financial 
transactions between promotional budgets and user wallets, maintaining strict 
integrity across the platform's redemption ledger.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.gift_codes.dtos import RedemptionResultDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.gift_codes.services")


class GiftCodeService:
    """Core domain service for gift code validation and promotional rewards."""

    def __init__(
        self,
        gift_repo: Any,
        wallet_service: Any,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._gift_repo: Final = gift_repo
        self._wallet_service: Final = wallet_service
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def redeem_code(self, user_id: int, code: str) -> RedemptionResultDTO:
        """Validates and processes a gift code redemption attempt."""
        
        # 1. Fetch and validate code status
        code_data = await self._gift_repo.get_active_code(code)
        if not code_data:
            return RedemptionResultDTO(success=False, message="Invalid or expired code.")

        if await self._gift_repo.has_already_redeemed(user_id, code_data.id):
            return RedemptionResultDTO(success=False, message="Code already redeemed.")

        # 2. Atomic Redemption Transaction
        try:
            async with self._transaction_repo.transaction():
                # Credit wallet
                await self._wallet_service.update_balance(
                    user_id, code_data.amount, "gift_code_redemption"
                )
                # Log redemption and update usage counters
                await self._gift_repo.record_redemption(user_id, code_data.id)
                await self._gift_repo.increment_usage(code_data.id)

            await self._event_bus.publish("gift_code.redeemed", {
                "user_id": user_id,
                "code_id": code_data.id,
                "amount": code_data.amount
            })

            return RedemptionResultDTO(
                success=True, 
                amount=code_data.amount, 
                message="Redemption successful."
            )

        except Exception as e:
            logger.error(f"Redemption transaction failed for {user_id}: {e}")
            return RedemptionResultDTO(success=False, message="System error during redemption.")
