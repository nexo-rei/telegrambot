from dataclasses import dataclass
from typing import Optional

@dataclass
class AuditEntryDTO:
    user_id: int = 0
    action: str = ""
    details: Optional[str] = None

@dataclass
class AuditStatsDTO:
    total_entries: int = 0
    recent_actions: int = 0
