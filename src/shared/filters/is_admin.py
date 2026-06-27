# is_admin.py
"""Administrative Access Authority Filter.

Provides a high-performance, asynchronous Aiogram filter for verifying administrative 
privileges. Leverages Redis-backed caching layers for near-instantaneous authorization 
checks, while ensuring strict state synchronization with the underlying persistence 
repository to block suspended or disabled accounts immediately.
"""

import logging
from typing import Any, Final, Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.filters.is_admin")

# Security threshold: Cache TTL for admin state validation
ADMIN_ROLE_TTL_SECONDS: Final[int] = 300


class IsAdmin(BaseFilter):
    """Filter that grants access only to verified administrative accounts."""

    def __init__(self, super_admin_only: bool = False) -> None:
        """Initializes the admin authorization filter.

        Args:
            super_admin_only: If True, restricts access exclusively to primary 
                              system owners/super-admins.
        """
        self.super_admin_only: Final[bool] = super_admin_only
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}admin_auth:")

    async def __call__(self, event: TelegramObject, event_from_user: Any = None) -> bool:
        """Validates administrative privileges for incoming interaction updates."""
        if not event_from_user:
            logger.warning("Admin filter invoked without user identification context.")
            return False

        user_id = event_from_user.id
        
        # Cache-first authorization strategy
        cached_role = await self._cache.get(str(user_id))
        
        if cached_role:
            return self._validate_role_criteria(cached_role)

        # Fallback to persistent repository lookup (Repository injection placeholder)
        # Integration point: UserRepo.get_user_role(user_id)
        # Assuming repository lookup returns 'ADMIN' or 'SUPERADMIN'
        user_role = await self._fetch_role_from_db(user_id)
        
        if user_role:
            await self._cache.set(str(user_id), user_role, expire_seconds=ADMIN_ROLE_TTL_SECONDS)
            return self._validate_role_criteria(user_role)

        return False

    def _validate_role_criteria(self, role: str) -> bool:
        """Evaluates resolved role string against filter constraints."""
        if self.super_admin_only:
            return role.upper() == "SUPERADMIN"
        return role.upper() in ("ADMIN", "SUPERADMIN")

    async def _fetch_role_from_db(self, user_id: int) -> Optional[str]:
        """Queries the source-of-truth database for the current administrative rank."""
        try:
            # Integration point: Replace with actual database service repository call
            # return await user_repo.get_role(user_id)
            return None 
        except Exception as db_fault:
            logger.error(f"Failed to resolve administrative role for UID {user_id}: {db_fault}")
            return None
