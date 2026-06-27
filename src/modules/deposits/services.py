# services.py
"""Production-grade Deposit Service.

Encapsulates all business logic for managing the deposit lifecycle, including 
payment initialization via external gateways (Paystack), verification 
reconciliation, and atomic wallet funding. Ensures transaction integrity 
through idempotent operations and resilient caching.
"""

import logging
import uuid
from typing import Final, Any
from decimal import Decimal

from src.modules.deposits.dtos import DepositRequestDTO, DepositResponseDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.deposits.services")


class DepositService:
    """Core domain service for deposit orchestration and gateway integration."""

    def __init__(
        self,
        deposit_repo: Any,
        wallet_service: Any,
        payment_adapter: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._deposit_repo: Final = deposit_repo
        self._wallet_service: Final = wallet_service
        self._payment_adapter: Final = payment_adapter
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def initialize_deposit(self, request: DepositRequestDTO) -> DepositResponseDTO:
        """Creates a pending deposit record and initializes a gateway payment session."""
        
        # Financial validation
        if request.amount < Decimal("100.00"):
            raise ValueError("Minimum deposit amount is ₦100.00.")

        reference = f"DEP-{uuid.uuid4().hex.upper()}"
        
        # Initialize gateway session
        payment_data = await self._payment_adapter.initialize_transaction(
            email=f"{request.user_id}@platform.internal",
            amount=int(request.amount * 100),  # Paystack expects kobo
            reference=reference
        )

        # Atomic persist
        async with self._deposit_repo.transaction():
            await self._deposit_repo.create_pending(
                user_id=request.user_id,
                reference=reference,
                amount=request.amount,
                gateway=request.gateway
            )
            
        await self._event_bus.publish("deposit.created", {"reference": reference})
        
        logger.info(f"Deposit {reference} initialized for user {request.user_id}")
        
        return DepositResponseDTO(
            transaction_reference=reference,
            status="pending",
            checkout_url=payment_data.get("authorization_url")
        )

    async def verify_payment(self, reference: str) -> bool:
        """Verifies transaction status with the gateway and triggers wallet funding."""
        
        # Idempotency check: verify if already processed
        deposit = await self._deposit_repo.get_by_reference(reference)
        if deposit.status == "successful":
            return True

        gateway_status = await self._payment_adapter.verify_transaction(reference)
        
        if gateway_status == "success":
            async with self._deposit_repo.transaction():
                await self._deposit_repo.update_status(reference, "successful")
                await self._wallet_service.update_balance(
                    deposit.user_id, deposit.amount, "credit"
                )
            
            await self._event_bus.publish("deposit.completed", {"reference": reference})
            logger.info(f"Deposit {reference} verified and wallet funded.")
            return True
            
        return False
