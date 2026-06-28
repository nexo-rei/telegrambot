from dataclasses import dataclass
from typing import Optional

@dataclass
class UserConfigurationDTO:
    user_id: int = 0
    language: str = "en"
    notifications_enabled: bool = True
    theme: Optional[str] = None
