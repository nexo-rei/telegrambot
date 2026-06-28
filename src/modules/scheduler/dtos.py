from dataclasses import dataclass
from typing import Optional

@dataclass
class JobStatusDTO:
    job_id: str = ""
    status: str = "idle"
    last_run: Optional[str] = None
    next_run: Optional[str] = None

@dataclass
class SchedulerHealthDTO:
    is_running: bool = False
    total_jobs: int = 0
    failed_jobs: int = 0
