# dtos.py
"""Production-grade Deposit Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing deposit 
requests, gateway responses, and transactional history. These DTOs provide 
a standardized schema for communication between the Deposit service, 
payment adapters (e.g., Paystack), and the persistence layer.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional
from datetime import datetime


@dataclass(frozen=True)
class DepositRequestDTO:
    """Request DTO for creating a new deposit record."""
    user_id: int
    amount: Decimal
    gateway: str
    currency: str = "NGN"


@dataclass(frozen=True)
class DepositResponseDTO:
    """Response DTO for a deposit initialization operation."""
    transaction_reference: str
    status: str
    checkout_url: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass(frozen=True)
class DepositDetailsDTO:
    """Detailed view of a single deposit transaction."""
    reference: str
    amount: Decimal
    fee: Decimal
    net_amount: Decimal
    status: str
    gateway: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class PaymentVerificationDTO:
    """DTO for gateway payment verification results."""
    reference: str
    gateway_transaction_id: str
    status: str
    verified_at: datetime = datetime.now()


@dataclass(frozen=True)
class DepositHistoryItemDTO:
    """DTO for representing an item in the user's deposit history list."""
    reference: str
    amount: Decimal
    status: str
    created_at: datetime
