from dataclasses import dataclass
from typing import Optional

@dataclass
class MediaMetadataDTO:
    media_id: str = ""
    media_type: str = ""
    file_size: int = 0
    url: Optional[str] = None

@dataclass
class MediaStatsDTO:
    total_media: int = 0
    total_size_bytes: int = 0
