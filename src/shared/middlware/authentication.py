# authentication.py
"""Enterprise Asynchronous Authentication Middleware.

Provides the primary security gateway for all incoming Telegram updates. Orchestrates
distributed session validation, user profile hydration, and permission resolution.

BUG FIX: The original RedisCacheClient usage assumed the client was already connected,
but `connect()` was never called. The `_execute_with_retry` method inside RedisCacheClient
calls `connect()` automatically if `self.client is None`, which is the correct fallback.
No change needed there - but `_fetch_user_from_db` was a permanent stub returning None,
meaning the middleware never injected real user data. Documented this as an integration
point that module consumers must wire up via dependency injection.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Final, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.exceptions import RedisError

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.middleware.authentication")

# Session cache TTL (1 hour) to balance security and performance
SESSION_CACHE_TTL: Final[int] = 3600


class AuthenticationMiddleware(BaseMiddleware):
    """Production-grade middleware for user identity validation and context injection."""

    def __init__(self, user_repo: Any = None) -> None:
        """Initializes the authentication gateway with distributed Redis session storage.

        Args:
            user_repo: Optional UserRepository instance for database fallback lookups.
                       If None, authentication falls back to cache-only (guest mode).
        """
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}session:")
        self._user_repo = user_repo

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Intercepts updates to hydrate the request context with user authentication data."""
        user: Optional[User] = data.get("event_from_user")

        # Non-user events (e.g., bot status updates) skip standard authentication
        if not user:
            return await handler(event, data)

        # Hydrate request data with authoritative user status
        auth_context = await self._resolve_user_context(user.id)

        if auth_context:
            data.update({
                "authenticated": True,
                "user_role": auth_context.get("role", "USER"),
                "account_status": auth_context.get("status", "ACTIVE"),
                "permissions": auth_context.get("permissions", []),
            })
        else:
            data.update({
                "authenticated": False,
                "user_role": "GUEST",
                "account_status": "UNREGISTERED",
            })

        return await handler(event, data)

    async def _resolve_user_context(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Resolves user session context using a tiered cache-to-database lookup."""
        cache_key = f"user_context:{user_id}"

        try:
            cached_context = await self._cache.get(cache_key)
            if cached_context:
                import json
                try:
                    return json.loads(cached_context)
                except (ValueError, TypeError):
                    pass

            # Persistent repository fallback (requires user_repo to be injected)
            user_data = await self._fetch_user_from_db(user_id)

            if user_data:
                import json
                await self._cache.set(
                    cache_key, json.dumps(user_data), expire_seconds=SESSION_CACHE_TTL
                )
                return user_data

        except RedisError as fault:
            logger.error(f"Authentication session cache failure for UID {user_id}: {fault}")

        return None

    async def _fetch_user_from_db(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Queries the source-of-truth database for account credentials and authorization data."""
        if self._user_repo is None:
            return None
        try:
            user = await self._user_repo.get_by_telegram_id(user_id)
            if not user:
                return None
            return {
                "role": "ADMIN" if user.is_admin else ("MODERATOR" if user.is_moderator else "USER"),
                "status": user.account_status,
                "permissions": [],
                "is_banned": user.is_banned,
                "is_active": user.is_active,
            }
        except Exception as db_fault:
            logger.error(f"Failed to fetch user context from DB for UID {user_id}: {db_fault}")
            return None
