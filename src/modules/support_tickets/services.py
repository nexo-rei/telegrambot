# services.py
"""Production-grade Support Ticket Service.

Encapsulates business logic for the full lifecycle of customer support 
inquiries, from initial creation and priority-based routing to resolution 
and archiving. Orchestrates state transitions, SLA tracking, and audit-logged 
communication threads within the platform's support infrastructure.
"""

import logging
from typing import Final, Any, Sequence
from datetime import datetime

from src.modules.support_tickets.dtos import TicketDTO, TicketResultDTO
from src.modules.support_tickets.exceptions import SupportTicketError

logger = logging.getLogger("investment_platform.modules.support_tickets.services")


class SupportTicketService:
    """Core domain service for support ticket orchestration and management."""

    def __init__(
        self,
        ticket_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._ticket_repo: Final = ticket_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_open_ticket_count(self, user_id: int) -> int:
        """Retrieves count of active tickets for the user, utilizing cache."""
        cache_key = f"ticket_count_{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached is not None:
            return int(cached)

        count = await self._ticket_repo.count_active(user_id)
        await self._cache.set(cache_key, count, ttl=300)
        return count

    async def create_ticket(
        self, user_id: int, subject: str, description: str
    ) -> TicketDTO:
        """Persists a new support ticket and triggers initial lifecycle events."""
        try:
            ticket = await self._ticket_repo.create(
                user_id=user_id,
                subject=subject,
                description=description,
                created_at=datetime.now()
            )
            
            # Emit event for staff notification or auto-assignment
            await self._event_bus.publish("support.ticket_created", {
                "ticket_id": ticket.id,
                "user_id": user_id
            })
            
            # Invalidate user ticket cache
            await self._cache.delete(f"ticket_count_{user_id}")
            
            return ticket
        except Exception as e:
            logger.error(f"Failed to create ticket for {user_id}: {e}")
            raise SupportTicketError("Persistence failure during ticket creation.")

    async def add_reply(
        self, ticket_id: str, sender_id: int, content: str
    ) -> bool:
        """Appends a new message to the ticket thread and updates state."""
        try:
            success = await self._ticket_repo.add_thread_message(
                ticket_id, sender_id, content
            )
            
            if success:
                await self._event_bus.publish("support.ticket_replied", {
                    "ticket_id": ticket_id,
                    "sender_id": sender_id
                })
            
            return success
        except Exception as e:
            logger.error(f"Failed to add reply to ticket {ticket_id}: {e}")
            raise SupportTicketError("Failed to update ticket thread.")
