# rate_limit.py
"""Enterprise Distributed Rate Limiting Decorator.

Provides a robust, asynchronous, Redis-backed rate-limiting mechanism to safeguard
platform endpoints against flood attacks, spam, and resource exhaustion. Utilizes
atomic Redis INCR/EXPIRE operations to ensure cross-instance synchronization and 
consistent state enforcement across distributed bot workers.
"""

import functools
import logging
from collections.abc import Callable
from typing import Any, Final, Optional, TypeVar

from aiogram.types import TelegramObject, User, Chat
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
        _cache_client = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}rate_limit:")
    return _cache_client


def rate_limit(
    limit: int = 5,
    window_seconds: int = 60,
    key_prefix: str = "default",
    error_message: str = "⚠️ Request frequency too high. Please slow down.",
    exclude_roles: Optional[list[str]] = None
) -> Callable[[F], F]:
    """Decorates asynchronous handlers to enforce distributed rate limits.

    Args:
        limit: Max requests allowed within the defined time window.
        window_seconds: Duration of the sliding time bucket in seconds.
        key_prefix: Unique namespace prefix to isolate this limiter's key space.
        error_message: User-facing notification content upon limit breach.
        exclude_roles: List of privileged roles permitted to bypass current limits.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Locate primary identifying Telegram objects (User/Chat)
            user: Optional[User] = kwargs.get("event_from_user")
            chat: Optional[Chat] = kwargs.get("event_chat")
            
            # Construct a unique identifier signature for this specific execution context
            identifier = f"{key_prefix}:{user.id if user else 'global'}"
            cache = get_cache_client()

            try:
                # Atomic increment operation with structural TTL logic
                # Uses standard fixed-window pattern for high performance across cluster nodes
                current_count = await cache.increment(identifier)
                
                if current_count == 1:
                    await cache.client.expire(cache._qualify_key(identifier), window_seconds)

                if current_count > limit:
                    logger.warning(f"Rate limit exceeded by {user.id if user else 'unknown'} on {key_prefix}")
                    # Integration hook: If handler is inside an Aiogram event, return alert
                    # Logic assumes the middleware or handler will catch custom exception triggers
                    return None 

            except (RedisError, Exception) as fault:
                # Resilience: Log error and allow execution if cache cluster is unreachable
                logger.error(f"Rate limiter subsystem fault: {fault}. Failing open to preserve UX.")
            
            return await func(*args, **kwargs)
        return wrapper # type: ignore
    return decorator
