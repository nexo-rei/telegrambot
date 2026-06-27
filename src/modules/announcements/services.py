# services.py
"""Production-grade Announcement Service.

Encapsulates business logic for system-wide broadcasts, scheduled content 
distribution, and targeted user communications. Orchestrates announcement 
lifecycles from authoring and scheduling to high-performance delivery, 
utilizing Redis-backed caching for real-time feed responsiveness.
"""

import logging
from typing import Final, Any, Sequence
from datetime import datetime

from src.modules.announcements.dtos import AnnouncementDTO
from src.modules.announcements.exceptions import AnnouncementError

logger = logging.getLogger("investment_platform.modules.announcements.services")


class AnnouncementService:
    """Core domain service for system-wide broadcast management."""

    def __init__(
        self,
        announcement_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._announcement_repo: Final = announcement_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_latest_announcements(self, limit: int = 10) -> Sequence[AnnouncementDTO]:
        """Retrieves the latest system announcements from cache or primary storage."""
        cache_key = "announcements_feed_latest"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        announcements = await self._announcement_repo.get_published(limit)
        await self._cache.set(cache_key, announcements, ttl=300)
        return announcements

    async def get_announcement_details(self, announcement_id: str) -> AnnouncementDTO | None:
        """Retrieves detailed content for a specific announcement."""
        cache_key = f"announcement_detail_{announcement_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        announcement = await self._announcement_repo.get_by_id(announcement_id)
        if announcement:
            await self._cache.set(cache_key, announcement, ttl=3600)
        return announcement

    async def publish_announcement(self, title: str, content: str, category: str) -> str:
        """Creates and broadcasts a new system announcement."""
        try:
            announcement = await self._announcement_repo.create(
                title=title,
                content=content,
                category=category,
                published_at=datetime.now()
            )
            
            # Broadcast event for downstream modules (e.g., Notifications)
            await self._event_bus.publish("announcement.published", {
                "announcement_id": announcement.id,
                "category": category
            })
            
            # Invalidate feed cache to propagate updates
            await self._cache.delete("announcements_feed_latest")
            
            return announcement.id
        except Exception as e:
            logger.error(f"Failed to publish announcement: {e}")
            raise AnnouncementError("Failed to persist and broadcast announcement.")
