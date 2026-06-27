# dtos.py
"""Production-grade Wallet Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing financial 
states and transactional requests within the wallet subsystem. These DTOs 
facilitate safe, serialized communication between the service layer, 
persistence modules, and payment gateways.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional
from datetime import datetime


@dataclass(frozen=True)
class WalletSummaryDTO:
    """Aggregated financial summary of a user's wallet state."""
    user_id: int
    available_balance: Decimal
    locked_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    last_updated: datetime = datetime.now()


@dataclass(frozen=True)
class DepositRequestDTO:
    """Request DTO for initiating a deposit process."""
    user_id: int
    amount: Decimal
    gateway: str
    currency: str = "NGN"


@dataclass(frozen=True)
class DepositResponseDTO:
    """Response DTO for a deposit operation."""
    transaction_reference: str
    status: str
    checkout_url: Optional[str] = None


@dataclass(frozen=True)
class WithdrawalRequestDTO:
    """Request DTO for initiating a withdrawal process."""
    user_id: int
    amount: Decimal
    destination_account: str
    currency: str = "NGN"


@dataclass(frozen=True)
class TransactionSummaryDTO:
    """Snapshot of a specific financial transaction."""
    reference: str
    amount: Decimal
    fee: Decimal
    net_amount: Decimal
    status: str
    created_at: datetime
    remarks: Optional[str] = None
