from dataclasses import dataclass
from decimal import Decimal

@dataclass
class DashboardStatsDTO:
    total_users: int = 0
    active_users: int = 0
    total_deposits: Decimal = Decimal("0.00")
    total_withdrawals: Decimal = Decimal("0.00")
    pending_withdrawals: int = 0
    total_investments: Decimal = Decimal("0.00")
