from dataclasses import dataclass
from typing import Optional

@dataclass
class ReviewQueueStatsDTO:
    pending_reviews: int = 0
    total_reviewed: int = 0

@dataclass
class ModeratorActivityDTO:
    moderator_id: int = 0
    actions_taken: int = 0
    last_active: Optional[str] = None
