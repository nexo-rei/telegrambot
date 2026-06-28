from dataclasses import dataclass
from typing import Optional

@dataclass
class LogEntryDTO:
    level: str = "INFO"
    message: str = ""
    module: Optional[str] = None
    user_id: Optional[int] = None
