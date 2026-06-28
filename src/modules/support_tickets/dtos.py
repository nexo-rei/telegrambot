from dataclasses import dataclass
from typing import Optional

@dataclass
class TicketDTO:
    ticket_id: int = 0
    user_id: int = 0
    subject: str = ""
    status: str = "open"
    message: Optional[str] = None

@dataclass
class TicketResultDTO:
    success: bool = False
    ticket_id: Optional[int] = None
    message: str = ""
