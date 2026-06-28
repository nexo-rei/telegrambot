# rate_limit.py
"""Enterprise Distributed Rate Limiting Decorator.

BUG FIX: `await cache.client.expire(...)` was called directly on `cache.client`
which may be None before `connect()` is called. Fixed by ensuring the connection
is established before accessing the raw client.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any, Final, Optional, TypeVar

from aiogram.types import User
from redis.exceptions import RedisError

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.decorators.rate_limit")

F = TypeVar("F", bound=Callable[..., Any])

# Global Singleton Cache Client for decorator access
_cache_client: Optional[RedisCacheClient] = None


def get_cache_client() -> RedisCacheClient:
    """Lazy-initializes the global Redis caching client instance."""
    global _cache_client
    if _cache_client is None:
        _cache_client = RedisCacheClient(
            prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}rate_limit:"
        )
    return _cache_client


def rate_limit(
    limit: int = 5,
    window_seconds: int = 60,
    key_prefix: str = "default",
    error_message: str = "⚠️ Request frequency too high. Please slow down.",
    exclude_roles: Optional[list[str]] = None,
) -> Callable[[F], F]:
    """Decorates asynchronous handlers to enforce distributed rate limits."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            user: Optional[User] = kwargs.get("event_from_user")

            identifier = f"{key_prefix}:{user.id if user else 'global'}"
            cache = get_cache_client()

            try:
                current_count = await cache.increment(identifier)

                if current_count == 1:
                    # BUG FIX: Ensure connection is established before accessing .client
                    if not cache.client:
                        await cache.connect()
                    await cache.client.expire(
                        cache._qualify_key(identifier), window_seconds
                    )

                if current_count > limit:
                    logger.warning(
                        f"Rate limit exceeded by {user.id if user else 'unknown'} on {key_prefix}"
                    )
                    return None

            except (RedisError, Exception) as fault:
                logger.error(
                    f"Rate limiter subsystem fault: {fault}. Failing open to preserve UX."
                )

            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator
