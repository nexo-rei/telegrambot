# __init__.py
"""Support Tickets Module Registry.

Aggregates and exposes the public interfaces for the platform's customer 
support and issue resolution subsystem. This module orchestrates the creation, 
tracking, and escalation of user inquiries, ensuring timely communication 
and professional handling of requests within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public support ticket components
from src.modules.support_tickets.handlers import SupportTicketHandlers
from src.modules.support_tickets.services import SupportTicketService
from src.modules.support_tickets.keyboards import SupportTicketKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "SupportTicketHandlers",
    "SupportTicketService",
    "SupportTicketKeyboards",
]

