# dtos.py
"""Production-grade Withdrawal Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing withdrawal 
requests, payout gateway responses, and transactional history. These DTOs 
facilitate standardized communication between the Withdrawal service, 
persistence layer, and external payout adapters (e.g., Paystack).
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional
from datetime import datetime


@dataclass(frozen=True)
class WithdrawalRequestDTO:
    """Request DTO for creating a new withdrawal request."""
    user_id: int
    amount: Decimal
    account_id: str
    currency: str = "NGN"


@dataclass(frozen=True)
class WithdrawalResponseDTO:
    """Response DTO for a withdrawal initialization operation."""
    reference: str
    status: str
    processed_at: Optional[datetime] = None


@dataclass(frozen=True)
class WithdrawalDetailsDTO:
    """Detailed view of a single withdrawal transaction."""
    reference: str
    amount: Decimal
    fee: Decimal
    net_amount: Decimal
    status: str
    account_number: str
    bank_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class PayoutInitializationDTO:
    """DTO for gateway payout session configuration."""
    transfer_recipient_code: str
    amount: Decimal
    reference: str
    reason: Optional[str] = None


@dataclass(frozen=True)
class WithdrawalHistoryItemDTO:
    """DTO for representing an item in the user's withdrawal history."""
    reference: str
    amount: Decimal
    status: str
    created_at: datetime
