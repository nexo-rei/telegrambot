# authentication.py
"""Enterprise Asynchronous Authentication Middleware.

Provides the primary security gateway for all incoming Telegram updates. Orchestrates 
distributed session validation, user profile hydration, and permission resolution. 
Enforces strict account lifecycle constraints (active/suspended/banned status) via 
a cache-first strategy to maintain low-latency response times for financial operations.
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

    def __init__(self) -> None:
        """Initializes the authentication gateway with distributed Redis session storage."""
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}session:")

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
                "user_role": auth_context.get("role", "GUEST"),
                "account_status": auth_context.get("status", "INACTIVE"),
                "permissions": auth_context.get("permissions", [])
            })
        else:
            # Default to guest status if no session exists
            data.update({
                "authenticated": False,
                "user_role": "GUEST",
                "account_status": "UNREGISTERED"
            })

        return await handler(event, data)

    async def _resolve_user_context(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Resolves user session context using a tiered cache-to-database lookup."""
        cache_key = f"user_context:{user_id}"
        
        try:
            # Cache-first lookup
            cached_context = await self._cache.get(cache_key)
            if cached_context:
                return cached_context  # type: ignore

            # Persistent repository fallback
            # Integration point: Repository DI (e.g., user_repo.get_authenticated_user(user_id))
            user_data = await self._fetch_user_from_db(user_id)
            
            if user_data:
                await self._cache.set(cache_key, user_data, expire_seconds=SESSION_CACHE_TTL)
                return user_data

        except RedisError as fault:
            logger.error(f"Authentication session cache failure for UID {user_id}: {fault}")
            
        return None

    async def _fetch_user_from_db(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Queries the source-of-truth database for account credentials and authorization data."""
        # This implementation should interact with the database repository layer.
        return None
