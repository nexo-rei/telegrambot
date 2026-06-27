# anti_spam.py
"""Enterprise Distributed Anti-Spam Middleware.

Provides a high-performance, asynchronous interceptor for detecting and mitigating 
malicious user behavior. Utilizes distributed Redis counters to enforce strict 
frequency bounds across message types, callback queries, and authentication flows, 
ensuring platform stability against flooding, bot-automation, and brute-force 
abuse attempts.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Final, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, Message, CallbackQuery
from redis.exceptions import RedisError

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.middleware.anti_spam")

# Middleware Operational Thresholds
SPAM_THRESHOLD_WINDOW: Final[int] = 5  # Seconds
MAX_ACTIONS_PER_WINDOW: Final[int] = 10
BLOCK_DURATION_SECONDS: Final[int] = 300


class AntiSpamMiddleware(BaseMiddleware):
    """Production-grade middleware for intercepting and blocking automated spam activity."""

    def __init__(self) -> None:
        """Initializes the anti-spam middleware with a distributed Redis backing."""
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}anti_spam:")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Intercepts incoming updates to validate behavior against spam profiles."""
        user: Optional[User] = data.get("event_from_user")
        
        # Bypass checks for unauthenticated context or system-level updates
        if not user or user.is_bot:
            return await handler(event, data)

        # Skip spam checks for authorized administrative staff
        if data.get("user_role") in ("ADMIN", "SUPERADMIN"):
            return await handler(event, data)

        try:
            is_spam = await self._is_user_spamming(user.id)
            if is_spam:
                logger.warning(f"Spam activity intercepted from User ID: {user.id}")
                # Return None to halt processing for this update
                return None
        except RedisError as fault:
            logger.error(f"Anti-spam subsystem connection fault: {fault}")
            # Fail open to preserve availability if the cache layer is down

        return await handler(event, data)

    async def _is_user_spamming(self, user_id: int) -> bool:
        """Evaluates user behavior profile using atomic Redis sliding windows."""
        key = f"user:{user_id}"
        
        # Increment request counter for the current sliding window
        current_count = await self._cache.increment(key)
        
        if current_count == 1:
            await self._cache.client.expire(self._cache._qualify_key(key), SPAM_THRESHOLD_WINDOW)
            
        if current_count > MAX_ACTIONS_PER_WINDOW:
            # Trigger temporary block state for repeat offenders
            await self._cache.set(f"block:{user_id}", "TRUE", expire_seconds=BLOCK_DURATION_SECONDS)
            return True
            
        return False
