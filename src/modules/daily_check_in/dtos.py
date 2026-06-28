from dataclasses import dataclass
from decimal import Decimal

@dataclass
class CheckInStatusDTO:
    user_id: int = 0
    streak: int = 0
    can_check_in: bool = True
    next_reward: Decimal = Decimal("0.00")

@dataclass
class CheckInResultDTO:
    success: bool = False
    reward: Decimal = Decimal("0.00")
    new_streak: int = 0
    message: str = ""
