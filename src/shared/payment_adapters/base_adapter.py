# base_adapter.py
"""Abstract Payment Gateway Interface.

Provides a standardized, polymorphic contract for all financial payment providers 
integrated within the platform. Defines essential lifecycle methods for payment 
initialization, verification, and webhook reconciliation to ensure that sub-adapters 
maintain strict architectural compliance and type-safe financial operations.
"""

import abc
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional, Final

@dataclass(frozen=True)
class PaymentResponse:
    """Standardized outcome data for payment initialization requests."""
    reference: str
    checkout_url: Optional[str]
    amount: Decimal
    currency: str = "NGN"

@dataclass(frozen=True)
class PaymentVerification:
    """Standardized result for payment verification operations."""
    is_successful: bool
    amount: Decimal
    reference: str
    provider_tx_id: Optional[str]
    raw_response: Dict[str, Any]

class PaymentAdapterError(Exception):
    """Base exception class for all payment gateway operations."""
    pass

class BasePaymentAdapter(abc.ABC):
    """Abstract base class governing the contract for all platform payment providers."""

    @abc.abstractmethod
    async def initialize_payment(
        self, 
        user_id: int, 
        amount: Decimal, 
        email: str, 
        reference: str
    ) -> PaymentResponse:
        """Initiates a payment session with the provider."""
        pass

    @abc.abstractmethod
    async def verify_payment(self, reference: str) -> PaymentVerification:
        """Verifies the final state of a transaction with the provider."""
        pass

    @abc.abstractmethod
    async def validate_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Validates the integrity and authenticity of an incoming provider webhook."""
        pass

    @abc.abstractmethod
    async def check_health(self) -> bool:
        """Returns True if the provider API is operational."""
        pass

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier for the payment provider."""
        pass

    def validate_currency(self, currency: str) -> bool:
        """Standard validator for ensuring supported currency codes."""
        return currency.upper() == "NGN"
