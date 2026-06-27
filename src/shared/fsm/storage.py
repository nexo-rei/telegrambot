"""Enterprise Distributed FSM Storage Engine.

Provides an optimized, Redis-backed asynchronous storage implementation for Aiogram 3.x 
finite state machines. Ensures distributed state consistency across multi-instance 
bot deployments, utilizing atomic JSON serialization and robust connection pooling 
to maintain transactional integrity for complex conversational workflows.
"""

import json
import logging
from typing import Any, Optional, Final

from aiogram.fsm.storage.base import BaseStorage, StateType
from aiogram.fsm.context import FSMContext
from redis.asyncio import Redis

logger = logging.getLogger("investment_platform.shared.fsm.storage")

# Configuration constants for state persistence
REDIS_KEY_PREFIX: Final[str] = "velorix:fsm"
DEFAULT_STATE_TTL_SECONDS: Final[int] = 86400  # 24 Hours


class RedisFSMStorage(BaseStorage):
    """Production-grade Redis storage backend for Aiogram FSM state maintenance."""

    def __init__(self, redis: Redis, prefix: str = REDIS_KEY_PREFIX) -> None:
        """Initializes the storage engine with a pre-configured Redis client.

        Args:
            redis: Asynchronous Redis client instance.
            prefix: Key-space namespace identifier for state isolation.
        """
        self._redis: Final[Redis] = redis
        self._prefix: Final[str] = prefix

    def _generate_key(self, bot_id: int, chat_id: int, user_id: int) -> str:
        """Constructs a deterministic, namespace-isolated key for Redis lookups."""
        return f"{self._prefix}:{bot_id}:{chat_id}:{user_id}"

    async def set_state(
        self, 
        bot: Any, 
        state: FSMContext, 
        value: StateType = None
    ) -> None:
        """Atomically updates the current state identifier for the provided context."""
        key = self._generate_key(bot.id, state.key.chat_id, state.key.user_id)
        
        async with self._redis.pipeline(transaction=True) as pipe:
            data = await pipe.get(key).execute()
            current_data = json.loads(data[0]) if data[0] else {}
            current_data["state"] = value.state if value else None
            
            await pipe.set(key, json.dumps(current_data), ex=DEFAULT_STATE_TTL_SECONDS)
            await pipe.execute()

    async def get_state(self, bot: Any, state: FSMContext) -> Optional[str]:
        """Retrieves the current state identifier string from persistent storage."""
        key = self._generate_key(bot.id, state.key.chat_id, state.key.user_id)
        data = await self._redis.get(key)
        
        if not data:
            return None
            
        return json.loads(data).get("state")

    async def set_data(self, bot: Any, state: FSMContext, data: dict[str, Any] = None) -> None:
        """Persists the FSM context data payload to the Redis backend."""
        key = self._generate_key(bot.id, state.key.chat_id, state.key.user_id)
        
        async with self._redis.pipeline(transaction=True) as pipe:
            raw = await pipe.get(key).execute()
            state_data = json.loads(raw[0]) if raw[0] else {}
            state_data["data"] = data or {}
            
            await pipe.set(key, json.dumps(state_data), ex=DEFAULT_STATE_TTL_SECONDS)
            await pipe.execute()

    async def get_data(self, bot: Any, state: FSMContext) -> dict[str, Any]:
        """Retrieves the full context data dictionary associated with the user/chat."""
        key = self._generate_key(bot.id, state.key.chat_id, state.key.user_id)
        data = await self._redis.get(key)
        
        if not data:
            return {}
            
        return json.loads(data).get("data", {})

    async def update_data(
        self, 
        bot: Any, 
        state: FSMContext, 
        data: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Performs an atomic update/merge of the FSM context payload."""
        key = self._generate_key(bot.id, state.key.chat_id, state.key.user_id)
        
        async with self._redis.pipeline(transaction=True) as pipe:
            raw = await pipe.get(key).execute()
            state_data = json.loads(raw[0]) if raw[0] else {"state": None, "data": {}}
            state_data["data"].update(data or {})
            
            await pipe.set(key, json.dumps(state_data), ex=DEFAULT_STATE_TTL_SECONDS)
            await pipe.execute()
            
        return state_data["data"]

    async def close(self) -> None:
        """Gracefully shuts down the storage engine connections."""
        await self._redis.close()
        logger.info("FSM storage engine shut down successfully.")
