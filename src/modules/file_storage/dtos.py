from dataclasses import dataclass
from typing import Optional

@dataclass
class FileMetadataDTO:
    filename: str = ""
    file_size: int = 0
    mime_type: Optional[str] = None
    url: Optional[str] = None

@dataclass
class StorageStatsDTO:
    total_files: int = 0
    total_size_bytes: int = 0
