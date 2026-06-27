# services.py
"""Production-grade Withdrawal Service.

Encapsulates all business logic for managing the withdrawal lifecycle, including 
payout initialization via external gateways (Paystack), atomic wallet 
balance deduction, and transactional reconciliation. Ensures financial 
integrity through ACID-compliant database operations and resilient caching.
"""

import logging
import uuid
from typing import Final, Any
from decimal import Decimal

from src.modules.withdrawals.dtos import WithdrawalRequestDTO, WithdrawalResponseDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.withdrawals.services")


class WithdrawalService:
    """Core domain service for withdrawal orchestration and payout processing."""

    def __init__(
        self,
        withdrawal_repo: Any,
        wallet_service: Any,
        payment_adapter: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._withdrawal_repo: Final = withdrawal_repo
        self._wallet_service: Final = wallet_service
        self._payment_adapter: Final = payment_adapter
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def submit_withdrawal(self, request: WithdrawalRequestDTO) -> WithdrawalResponseDTO:
        """Validates balance, deducts funds, and initiates the payout process."""
        
        # Financial validation
        summary = await self._wallet_service.get_wallet_summary(request.user_id)
        if request.amount > summary.available_balance:
            raise ValueError("Insufficient available balance for this withdrawal.")

        if request.amount < Decimal("1000.00"):
            raise ValueError("Minimum withdrawal amount is ₦1,000.00.")

        reference = f"WDR-{uuid.uuid4().hex.upper()}"

        # Atomic transaction: Debit wallet and create pending withdrawal
        async with self._withdrawal_repo.transaction():
            await self._wallet_service.update_balance(
                request.user_id, -request.amount, "debit"
            )
            await self._withdrawal_repo.create(
                user_id=request.user_id,
                reference=reference,
                amount=request.amount,
                account_id=request.account_id
            )

        # Trigger asynchronous payout initialization
        await self._event_bus.publish("withdrawal.created", {"reference": reference})
        
        logger.info(f"Withdrawal {reference} created for user {request.user_id}")
        
        return WithdrawalResponseDTO(reference=reference, status="pending")

    async def process_payout(self, reference: str) -> bool:
        """Executes the actual external transfer via payment gateway."""
        
        withdrawal = await self._withdrawal_repo.get_by_reference(reference)
        
        try:
            payout_result = await self._payment_adapter.initiate_transfer(
                amount=int(withdrawal.amount * 100),
                recipient_code=withdrawal.account_id,
                reference=reference
            )
            
            await self._withdrawal_repo.update_status(reference, "processing")
            await self._event_bus.publish("withdrawal.payout_initialized", {"reference": reference})
            return True
            
        except Exception as e:
            # Revert funds if payout fails to initialize
            await self._wallet_service.update_balance(
                withdrawal.user_id, withdrawal.amount, "credit"
            )
            await self._withdrawal_repo.update_status(reference, "failed")
            logger.error(f"Payout failed for {reference}: {e}")
            return False
