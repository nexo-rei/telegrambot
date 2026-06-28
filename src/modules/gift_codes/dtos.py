from dataclasses import dataclass
from decimal import Decimal

@dataclass
class RedemptionResultDTO:
    success: bool = False
    code: str = ""
    reward_amount: Decimal = Decimal("0.00")
    message: str = ""
