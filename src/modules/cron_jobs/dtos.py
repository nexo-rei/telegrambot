from dataclasses import dataclass
from typing import Optional

@dataclass
class CronStatsDTO:
    total_jobs: int = 0
    running_jobs: int = 0
    failed_jobs: int = 0

@dataclass
class CronJobEntryDTO:
    job_name: str = ""
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    status: str = "idle"
