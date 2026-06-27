# dtos.py
"""Production-grade Investment Plan Data Transfer Objects (DTOs).

Defines immutable, strongly-typed data structures for representing investment 
products, purchase requests, and ROI projections. These DTOs facilitate 
standardized communication between the investment service, persistence layer, 
and the user interface modules.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional
from datetime import datetime


@dataclass(frozen=True)
class InvestmentPlanDTO:
    """Representation of an investment product and its financial parameters."""
    plan_id: str
    name: str
    description: str
    min_amount: Decimal
    max_amount: Decimal
    roi_percentage: Decimal
    duration_days: int
    is_active: bool = True
    is_featured: bool = False


@dataclass(frozen=True)
class InvestmentPurchaseRequestDTO:
    """Request DTO for initiating an investment purchase."""
    user_id: int
    plan_id: str
    amount: Decimal
    currency: str = "NGN"


@dataclass(frozen=True)
class InvestmentPurchaseResponseDTO:
    """Response DTO confirming an investment activation."""
    investment_id: str
    status: str
    purchase_timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class InvestmentPreviewDTO:
    """DTO for displaying projected returns before final purchase."""
    plan_name: str
    investment_amount: Decimal
    total_expected_roi: Decimal
    estimated_maturity_value: Decimal
    maturity_date: datetime


@dataclass(frozen=True)
class InvestmentCalculatorDTO:
    """DTO for input parameters in financial projections."""
    amount: Decimal
    duration_days: int
    roi_percentage: Decimal
