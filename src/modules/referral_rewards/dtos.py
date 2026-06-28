from dataclasses import dataclass
from decimal import Decimal

@dataclass
class RewardSummaryDTO:
    user_id: int = 0
    total_rewards: Decimal = Decimal("0.00")
    pending_rewards: Decimal = Decimal("0.00")
    claimed_rewards: Decimal = Decimal("0.00")

@dataclass
class ClaimResultDTO:
    success: bool = False
    amount: Decimal = Decimal("0.00")
    message: str = ""
