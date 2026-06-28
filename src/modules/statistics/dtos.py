from dataclasses import dataclass
from decimal import Decimal

@dataclass
class PlatformOverviewDTO:
    total_users: int = 0
    active_investors: int = 0
    total_invested: Decimal = Decimal("0.00")
    total_paid_out: Decimal = Decimal("0.00")
    platform_profit: Decimal = Decimal("0.00")
