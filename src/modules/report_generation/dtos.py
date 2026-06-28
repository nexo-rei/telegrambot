from dataclasses import dataclass
from typing import Optional

@dataclass
class ReportMetadataDTO:
    report_id: str = ""
    report_type: str = ""
    status: str = "pending"
    file_url: Optional[str] = None

@dataclass
class ReportRequestDTO:
    report_type: str = ""
    user_id: int = 0
    date_from: Optional[str] = None
    date_to: Optional[str] = None
