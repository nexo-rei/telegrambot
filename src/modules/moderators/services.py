# services.py
"""Production-grade Moderator Service.

Encapsulates business logic for platform integrity, compliance monitoring, and 
operational review workflows. Orchestrates user enforcement actions, financial 
transaction verification, and ticket escalation queues to maintain system safety 
and high-quality customer support within the investment platform.
"""

import logging
from typing import Final, Any
from datetime import datetime

from src.modules.moderators.dtos import ReviewQueueStatsDTO, ModeratorActivityDTO
from src.modules.moderators.exceptions import ModeratorActionError

logger = logging.getLogger("investment_platform.modules.moderators.services")


class ModeratorService:
    """Core domain service for moderation operations and platform compliance."""

    def __init__(
        self,
        moderator_repo: Any,
        user_repo: Any,
        financial_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._moderator_repo: Final = moderator_repo
        self._user_repo: Final = user_repo
        self._financial_repo: Final = financial_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def is_moderator(self, user_id: int) -> bool:
        """Validates current user's authorization to perform moderator actions."""
        return await self._moderator_repo.has_permission(user_id)

    async def get_review_queue_stats(self) -> ReviewQueueStatsDTO:
        """Aggregates real-time pending moderation workload statistics."""
        cache_key = "mod_queue_stats"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        stats = ReviewQueueStatsDTO(
            pending_deposits=await self._financial_repo.count_pending_deposits(),
            pending_withdrawals=await self._financial_repo.count_pending_withdrawals(),
            assigned_tickets=await self._moderator_repo.count_assigned_tickets()
        )
        
        await self._cache.set(cache_key, stats, ttl=60)
        return stats

    async def suspend_user(self, moderator_id: int, target_user_id: int, reason: str) -> bool:
        """Executes user suspension with mandatory audit logging and event dispatch."""
        if not await self.is_moderator(moderator_id):
            raise ModeratorActionError("Unauthorized moderation attempt.")

        try:
            async with self._user_repo.transaction():
                success = await self._user_repo.update_status(target_user_id, "suspended")
                if success:
                    await self._moderator_repo.record_action(
                        moderator_id, "suspend", target_user_id, reason, datetime.now()
                    )
                    await self._event_bus.publish("moderator.user_suspended", {
                        "user_id": target_user_id,
                        "moderator_id": moderator_id,
                        "reason": reason
                    })
                    await self._cache.delete("mod_queue_stats")
            return success
        except Exception as e:
            logger.error(f"Moderation suspension failed: {e}")
            raise ModeratorActionError("Persistence failure during user suspension.")
