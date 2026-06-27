# is_registered.py
"""Registered Account Authentication Filter.

Provides a high-performance, asynchronous Aiogram filter for verifying user registration 
status and account operational health. Leverages Redis-backed caching to minimize 
database I/O, ensuring that only active, verified, and non-suspended users can interact 
with the platform's protected financial and dashboard surfaces.
"""

import logging
from typing import Any, Final, Optional

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.filters.is_registered")

# Cache expiry for registered account state to prevent repeated DB polling
USER_REG_STATE_TTL_SECONDS: Final[int] = 600


class IsRegistered(BaseFilter):
    """Filter that validates user account registration and active standing status."""

    def __init__(self, check_verification: bool = False) -> None:
        """Initializes the registration filter.

        Args:
            check_verification: If True, requires full KYC/Email verification 
                                status to pass the filter.
        """
        self.check_verification: Final[bool] = check_verification
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}user_auth:")

    async def __call__(self, event: TelegramObject, event_from_user: Any = None) -> bool:
        """Validates if the user is registered and authorized to access application tiers."""
        if not event_from_user:
            logger.warning("Registration filter invoked without valid user context.")
            return False

        user_id = event_from_user.id
        cache_key = f"reg_status:{user_id}"

        # Cache-first authorization strategy
        cached_status = await self._cache.get(cache_key)
        
        if cached_status is not None:
            return cached_status == "ACTIVE"

        # Database lookup fallback (Dependency Injection integration point)
        user_record = await self._fetch_user_status_from_db(user_id)
        
        if user_record and self._is_account_authorized(user_record):
            # Update cache with active state
            await self._cache.set(cache_key, "ACTIVE", expire_seconds=USER_REG_STATE_TTL_SECONDS)
            return True

        return False

    def _is_account_authorized(self, record: dict[str, Any]) -> bool:
        """Validates account state integrity and non-suspended status."""
        is_active = record.get("status") == "ACTIVE"
        is_verified = True if not self.check_verification else record.get("verified", False)
        return is_active and is_verified

    async def _fetch_user_status_from_db(self, user_id: int) -> Optional[dict[str, Any]]:
        """Queries the source-of-truth repository for account registration state."""
        try:
            # Integration point: Replace with actual UserRepo call
            # return await user_repo.get_user_auth_status(user_id)
            return None
        except Exception as db_fault:
            logger.error(f"Failed to resolve registration status for UID {user_id}: {db_fault}")
            return None
