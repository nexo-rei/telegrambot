# rate_limiter.py
"""Enterprise Distributed Rate Limiter Middleware.

BUG FIX: `self._cache.client.pipeline(...)` was called directly on the client
attribute which may be None before `connect()` is called. Fixed by ensuring
the connection is established before accessing the raw client.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Final, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.exceptions import RedisError

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.middleware.rate_limiter")

# Rate Limiting Configuration Parameters
REQUESTS_PER_MINUTE: Final[int] = 60
RATE_LIMIT_WINDOW: Final[int] = 60  # seconds


class RateLimiterMiddleware(BaseMiddleware):
    """Production-grade middleware for throttling incoming user traffic."""

    def __init__(self) -> None:
        """Initializes the rate limiter with distributed Redis state management."""
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}rate_limit:")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Intercepts updates to enforce frequency boundaries on interaction."""
        user: Optional[User] = data.get("event_from_user")

        if not user:
            return await handler(event, data)

        # Administrative/VIP tiers enjoy higher or unlimited quotas
        user_role = data.get("user_role", "GUEST")
        if user_role in ("ADMIN", "SUPERADMIN", "VIP"):
            return await handler(event, data)

        try:
            limit_exceeded = await self._check_rate_limit(user.id)
            if limit_exceeded:
                logger.warning(f"Rate limit exceeded for UID: {user.id}")
                return None
        except RedisError as fault:
            logger.error(f"Rate limiter subsystem fault: {fault}")
            # Fail-open strategy to prioritize system availability

        return await handler(event, data)

    async def _check_rate_limit(self, user_id: int) -> bool:
        """Enforces a sliding window rate limit using atomic Redis operations.

        BUG FIX: Original called `self._cache.client.pipeline(...)` directly.
        `self._cache.client` is None until `connect()` is called. Fixed by
        ensuring connection is established first.
        """
        key = self._cache._qualify_key(f"user:{user_id}")

        # Ensure connection is alive before accessing raw client
        if not self._cache.client:
            await self._cache.connect()

        async with self._cache.client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, RATE_LIMIT_WINDOW)
            results = await pipe.execute()

        current_count = results[0]
        return current_count > REQUESTS_PER_MINUTE
