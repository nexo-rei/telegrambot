# dtos.py
"""Production-grade Active Investment Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing active 
investment positions, progress tracking, and earnings summaries. These DTOs 
ensure consistent data interchange between the portfolio management service, 
the persistence layer, and reporting/analytics modules.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional
from datetime import datetime


@dataclass(frozen=True)
class InvestmentDetailsDTO:
    """Detailed immutable representation of an active investment position."""
    investment_id: str
    amount: Decimal
    status: str
    progress_percentage: Decimal
    daily_earnings: Decimal
    currency: str = "NGN"
    start_date: Optional[datetime] = None
    maturity_date: Optional[datetime] = None


@dataclass(frozen=True)
class InvestmentProgressDTO:
    """Represents real-time yield and duration progress of an investment."""
    investment_id: str
    elapsed_days: int
    total_duration: int
    roi_earned: Decimal
    remaining_roi: Decimal
    health_status: str = "active"


@dataclass(frozen=True)
class EarningsSummaryDTO:
    """Aggregated earnings data for an active investment position."""
    investment_id: str
    total_earnings: Decimal
    pending_earnings: Decimal
    last_distribution_date: Optional[datetime] = None
    next_distribution_date: Optional[datetime] = None


@dataclass(frozen=True)
class MaturityInformationDTO:
    """DTO for tracking investment maturity and final projected value."""
    investment_id: str
    maturity_date: datetime
    expected_maturity_value: Decimal
    is_auto_reinvest_enabled: bool = False
