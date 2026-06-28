from dataclasses import dataclass
from typing import Optional

@dataclass
class FraudStatsDTO:
    flagged_users: int = 0
    blocked_users: int = 0
    total_alerts: int = 0

@dataclass
class ActivityRecordDTO:
    user_id: int = 0
    action: str = ""
    risk_level: str = "low"
    details: Optional[str] = None
