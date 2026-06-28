from dataclasses import dataclass
from decimal import Decimal

@dataclass
class EarningsSummaryDTO:
    user_id: int = 0
    daily_earnings: Decimal = Decimal("0.00")
    total_earned: Decimal = Decimal("0.00")

@dataclass
class ClaimResultDTO:
    success: bool = False
    amount: Decimal = Decimal("0.00")
    message: str = ""
