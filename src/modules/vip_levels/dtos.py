from dataclasses import dataclass
from decimal import Decimal

@dataclass
class VIPStatusDTO:
    user_id: int = 0
    current_level: int = 0
    level_name: str = "Basic"
    total_invested: Decimal = Decimal("0.00")

@dataclass
class UpgradeResultDTO:
    success: bool = False
    new_level: int = 0
    new_level_name: str = ""
    message: str = ""
