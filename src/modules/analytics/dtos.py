from dataclasses import dataclass
from decimal import Decimal

@dataclass
class ExecutiveSummaryDTO:
    total_revenue: Decimal = Decimal("0.00")
    active_users: int = 0
    conversion_rate: float = 0.0

@dataclass
class FraudIndicatorDTO:
    user_id: int = 0
    risk_score: float = 0.0
    flags: list = None
    def __post_init__(self):
        if self.flags is None: self.flags = []
