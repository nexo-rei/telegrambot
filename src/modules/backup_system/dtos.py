from dataclasses import dataclass
from typing import Optional

@dataclass
class BackupStatusDTO:
    is_running: bool = False
    last_backup: Optional[str] = None
    status: str = "idle"

@dataclass
class BackupEntryDTO:
    filename: str = ""
    size_bytes: int = 0
    created_at: Optional[str] = None
