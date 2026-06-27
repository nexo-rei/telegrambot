# dtos.py
"""Production-grade Transaction Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing financial 
transaction records, search parameters, and reporting outputs. These DTOs 
ensure consistent data interchange between the transaction ledger, the 
persistence layer, and reporting/export modules.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Final, Optional, List
from datetime import datetime


@dataclass(frozen=True)
class TransactionDetailsDTO:
    """Detailed immutable representation of a single transaction record."""
    transaction_id: str
    user_id: int
    reference: str
    type: str
    status: str
    amount: Decimal
    fee: Decimal
    net_amount: Decimal
    currency: str = "NGN"
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class TransactionHistoryItemDTO:
    """Concise representation of a transaction for list/history views."""
    reference: str
    type: str
    amount: Decimal
    status: str
    created_at: datetime


@dataclass(frozen=True)
class TransactionFilterDTO:
    """Request DTO for filtering and paginating transaction records."""
    page_number: int = 1
    page_size: int = 20
    transaction_types: Optional[List[str]] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass(frozen=True)
class StatementRequestDTO:
    """Request DTO for generating financial account statements."""
    user_id: int
    start_date: datetime
    end_date: datetime
    format: str = "PDF"


@dataclass(frozen=True)
class TransactionStatisticsDTO:
    """Aggregated financial metrics for a user's transaction history."""
    total_inflow: Decimal
    total_outflow: Decimal
    transaction_count: int
    net_position: Decimal
