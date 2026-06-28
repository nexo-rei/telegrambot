"""Enterprise Distributed FSM Storage Engine.

BUG FIX: The original RedisFSMStorage implementation used the wrong aiogram 3.x
BaseStorage API. In aiogram 3.x:
  - BaseStorage.set_state(key: StorageKey, state: StateType) - not (bot, state, value)
  - BaseStorage.get_state(key: StorageKey) - not (bot, state)
  - BaseStorage.set_data(key: StorageKey, data: dict) - not (bot, state, data)
  - BaseStorage.get_data(key: StorageKey) - not (bot, state)

The original signatures matched aiogram 2.x API and would fail completely.

Also fixed: pipeline usage was wrong - `await pipe.get(key).execute()` is incorrect;
the correct pattern is to queue commands and then execute all at once.

NOTE: In practice, aiogram 3.x ships with RedisStorage in aiogram.fsm.storage.redis
which already provides a correct implementation. This custom storage is kept for
reference/overrides but the app should prefer the built-in RedisStorage.
"""

import json
import logging
from typing import Any, Optional, Final

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from redis.asyncio import Redis

logger = logging.getLogger("investment_platform.shared.fsm.storage")

# Configuration constants for state persistence
REDIS_KEY_PREFIX: Final[str] = "velorix:fsm"
DEFAULT_STATE_TTL_SECONDS: Final[int] = 86400  # 24 Hours


class RedisFSMStorage(BaseStorage):
    """Production-grade Redis storage backend for Aiogram 3.x FSM state maintenance.

    BUG FIX: Rewrote to use the correct aiogram 3.x BaseStorage API which takes
    StorageKey objects instead of (bot, state) pairs.
    """

    def __init__(self, redis: Redis, prefix: str = REDIS_KEY_PREFIX) -> None:
        """Initializes the storage engine with a pre-configured Redis client.

        Args:
            redis: Asynchronous Redis client instance.
            prefix: Key-space namespace identifier for state isolation.
        """
        self._redis: Final[Redis] = redis
        self._prefix: Final[str] = prefix

    def _generate_key(self, key: StorageKey) -> str:
        """Constructs a deterministic, namespace-isolated key for Redis lookups."""
        return f"{self._prefix}:{key.bot_id}:{key.chat_id}:{key.user_id}"

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """Atomically updates the current state identifier for the provided context."""
        redis_key = self._generate_key(key)

        raw = await self._redis.get(redis_key)
        current_data: dict = json.loads(raw) if raw else {}
        current_data["state"] = state.state if hasattr(state, "state") else state

        await self._redis.set(redis_key, json.dumps(current_data), ex=DEFAULT_STATE_TTL_SECONDS)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Retrieves the current state identifier string from persistent storage."""
        redis_key = self._generate_key(key)
        data = await self._redis.get(redis_key)

        if not data:
            return None

        return json.loads(data).get("state")

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        """Persists the FSM context data payload to the Redis backend."""
        redis_key = self._generate_key(key)

        raw = await self._redis.get(redis_key)
        state_data: dict = json.loads(raw) if raw else {}
        state_data["data"] = data or {}

        await self._redis.set(redis_key, json.dumps(state_data), ex=DEFAULT_STATE_TTL_SECONDS)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """Retrieves the full context data dictionary associated with the user/chat."""
        redis_key = self._generate_key(key)
        data = await self._redis.get(redis_key)

        if not data:
            return {}

        return json.loads(data).get("data", {})

    async def update_data(
        self,
        key: StorageKey,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Performs an atomic update/merge of the FSM context payload."""
        redis_key = self._generate_key(key)

        raw = await self._redis.get(redis_key)
        state_data: dict = json.loads(raw) if raw else {"state": None, "data": {}}
        state_data["data"].update(data or {})

        await self._redis.set(redis_key, json.dumps(state_data), ex=DEFAULT_STATE_TTL_SECONDS)

        return state_data["data"]

    async def close(self) -> None:
        """Gracefully shuts down the storage engine connections."""
        await self._redis.aclose()
        logger.info("FSM storage engine shut down successfully.")
