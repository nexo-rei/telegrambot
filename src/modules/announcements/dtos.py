from dataclasses import dataclass
from typing import Optional

@dataclass
class AnnouncementDTO:
    title: str = ""
    message: str = ""
    is_active: bool = True
    target_audience: Optional[str] = None
