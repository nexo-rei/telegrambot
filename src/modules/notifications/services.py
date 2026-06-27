# services.py
"""Production-grade Notification Service.

Encapsulates business logic for event-driven system communications, alert 
dispatching, and user preference management. Orchestrates the lifecycle of 
notifications from creation and persistence to delivery and status tracking, 
ensuring low-latency access via Redis caching and reliable state management.
"""

import logging
from typing import Final, Any, Sequence

from src.modules.notifications.dtos import NotificationDTO
from src.modules.notifications.exceptions import NotificationError

logger = logging.getLogger("investment_platform.modules.notifications.services")


class NotificationService:
    """Core domain service for managing notification lifecycles and delivery."""

    def __init__(
        self,
        notification_repo: Any,
        preference_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._notification_repo: Final = notification_repo
        self._preference_repo: Final = preference_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_recent_notifications(
        self, user_id: int, limit: int = 10
    ) -> Sequence[NotificationDTO]:
        """Retrieves a cached list of recent notifications for the user."""
        cache_key = f"notifications_{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        notifications = await self._notification_repo.get_by_user(user_id, limit)
        await self._cache.set(cache_key, notifications, ttl=60)
        return notifications

    async def mark_as_read(self, user_id: int, notification_id: str) -> bool:
        """Updates the read status of a notification and invalidates cache."""
        try:
            success = await self._notification_repo.update_read_status(
                user_id, notification_id, is_read=True
            )
            
            if success:
                await self._cache.delete(f"notifications_{user_id}")
                await self._event_bus.publish("notification.read", {
                    "user_id": user_id,
                    "notification_id": notification_id
                })
            
            return success
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            raise NotificationError("Persistence failure during status update.")

    async def create_notification(
        self, user_id: int, title: str, message: str, category: str
    ) -> None:
        """Creates a new notification entry and triggers delivery events."""
        try:
            notification = await self._notification_repo.create(
                user_id, title, message, category
            )
            
            await self._event_bus.publish("notification.created", {
                "user_id": user_id,
                "notification_id": notification.id,
                "category": category
            })
            
            # Invalidate cache to reflect new content immediately
            await self._cache.delete(f"notifications_{user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create notification for {user_id}: {e}")
            raise NotificationError("Failed to persist new notification.")
