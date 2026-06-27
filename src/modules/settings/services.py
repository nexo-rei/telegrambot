# services.py
"""Production-grade Settings Service.

Encapsulates business logic for user-specific configuration, preference 
lifecycle management, and application-wide parameter synchronization. Ensures 
atomic updates, cache consistency via Redis, and secure access control for 
platform settings within the Nigerian Investment Platform architecture.
"""

import logging
from typing import Final, Any, Optional

from src.modules.settings.dtos import UserConfigurationDTO
from src.modules.settings.exceptions import SettingsProcessingError

logger = logging.getLogger("investment_platform.modules.settings.services")


class SettingsService:
    """Core domain service for user preference and configuration management."""

    def __init__(
        self,
        repository: Any,
        cache_manager: Any,
        event_bus: Any,
        audit_logger: Any
    ) -> None:
        self._repo: Final = repository
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._audit: Final = audit_logger

    async def get_user_configuration(self, user_id: int) -> UserConfigurationDTO:
        """Retrieves user settings, utilizing a cache-first retrieval strategy."""
        cache_key = f"user_settings:{user_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            config = await self._repo.fetch_user_settings(user_id)
            await self._cache.set(cache_key, config, ttl=86400)
            return config
        except Exception as e:
            logger.error(f"Failed to fetch configuration for user {user_id}: {e}")
            raise SettingsProcessingError("Configuration retrieval failed.")

    async def toggle_setting(self, user_id: int, key: str) -> bool:
        """Atomically updates a specific user preference and invalidates cache."""
        try:
            current_config = await self.get_user_configuration(user_id)
            new_value = not getattr(current_config, key)
            
            # Persist state change
            await self._repo.update_user_preference(user_id, key, new_value)
            
            # Invalidate and update cache
            await self._cache.delete(f"user_settings:{user_id}")
            
            # Audit and event propagation
            await self._audit.log(user_id, f"preference_changed:{key}")
            await self._event_bus.publish("settings.updated", {"user_id": user_id, "key": key})
            
            return new_value
        except Exception as e:
            logger.error(f"Error toggling setting {key} for user {user_id}: {e}")
            raise SettingsProcessingError("Preference update failed.")

    async def reset_to_defaults(self, user_id: int) -> None:
        """Resets all platform preferences to system-defined defaults."""
        try:
            await self._repo.reset_settings(user_id)
            await self._cache.delete(f"user_settings:{user_id}")
            await self._event_bus.publish("settings.reset", {"user_id": user_id})
        except Exception as e:
            logger.error(f"Failed to reset settings for {user_id}: {e}")
            raise SettingsProcessingError("Configuration reset operation failed.")
