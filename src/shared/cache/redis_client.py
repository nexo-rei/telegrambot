# redis_client.py
"""Asynchronous Redis Client Subsystem.

Provides an enterprise-grade, high-performance interface for caching, distributed data
structures, and connection pool lifecycle management. Wraps native redis.asyncio commands 
with protective automatic retry loops, custom connection monitors, serialization matrices, 
and explicit prefix namespace isolation blocks.
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any, Final, Optional

from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.client import PubSub
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
)

logger = logging.getLogger("investment_platform.shared.cache.redis")

# Structural Resilience Constraints Matrix
MAX_RECONNECT_ATTEMPTS: Final[int] = 5
BASE_RETRY_BACKOFF_SECONDS: Final[float] = 0.5
REDIS_SOCKET_TIMEOUT_SECONDS: Final[float] = 5.0


class RedisCacheClient:
    """Centralized production-ready client governing asynchronous Redis operations."""

    def __init__(self, prefix_namespace: str = "velorix:") -> None:
        """Initializes structural connection pooling structures.

        Args:
            prefix_namespace: Enforces global cryptographic or structural key boundaries.
        """
        self.namespace: Final[str] = prefix_namespace
        self._pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        self._lock: Final[asyncio.Lock] = asyncio.Lock()

    def _qualify_key(self, raw_key: str) -> str:
        """Appends the global operational namespace onto a raw string key safely."""
        return f"{self.namespace}{raw_key}"

    async def connect(self) -> None:
        """Establishes persistent non-blocking asynchronous connection pools."""
        async with self._lock:
            if self.client is not None:
                return

            logger.info(f"Establishing active connection pool to Redis cluster engine at {REDIS_HOST}:{REDIS_PORT}...")
            try:
                self._pool = ConnectionPool(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD,
                    db=REDIS_DB,
                    socket_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
                    socket_connect_timeout=REDIS_SOCKET_TIMEOUT_SECONDS,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                self.client = Redis(connection_pool=self._pool)
                await self.client.ping()
                logger.info("Asynchronous Redis connection matrix verified and running.")
            except RedisError as fault:
                logger.critical(f"Total bootstrap collapse across caching infrastructure sockets: {fault}", exc_info=True)
                raise fault

    async def disconnect(self) -> None:
        """Gracefully drains connection pools and closes open asynchronous channels."""
        async with self._lock:
            if not self.client:
                return
            
            logger.info("Disconnecting caching client pool sockets programmatically...")
            try:
                await self.client.close()
                if self._pool:
                    await self._pool.disconnect()
            except Exception as teardown_fault:
                logger.error(f"Error encountered during cache socket destruction pipeline: {teardown_fault}")
            finally:
                self.client = None
                self._pool = None
                logger.info("Active Redis context pool destroyed cleanly.")

    async def _execute_with_retry(self, action_callable: Callable[[Redis], Coroutine[Any, Any, Any]]) -> Any:
        """Wraps low-level infrastructure transactions with automatic linear backoff retry logic."""
        if not self.client:
            await self.connect()

        attempts = 0
        while attempts < MAX_RECONNECT_ATTEMPTS:
            try:
                return await action_callable(self.client)
            except (ConnectionError, TimeoutError) as network_error:
                attempts += 1
                backoff = BASE_RETRY_BACKOFF_SECONDS * attempts
                logger.warning(f"Cache network interruption caught (Attempt {attempts}/{MAX_RECONNECT_ATTEMPTS}). Retrying in {backoff}s. Error: {network_error}")
                await asyncio.sleep(backoff)
            except RedisError as redis_fault:
                logger.error(f"Execution error within underlying data driver engine boundaries: {redis_fault}")
                raise redis_fault

        logger.critical("Resilience threshold breached. Caching cluster node is completely unresponsive.")
        raise ConnectionError("Unable to satisfy operational command sequence. Target Redis server down.")

    # --- Structural Key-Value Cache Operations API ---

    async def get(self, key: str) -> Optional[str]:
        """Fetches a string payload match from the cache matrix using explicit namespaces."""
        qualified = self._qualify_key(key)
        async def _get(redis_inst: Redis) -> Any:
            val = await redis_inst.get(qualified)
            return val.decode("utf-8") if val else None
        return await self._execute_with_retry(_get)

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Stores a string payload match within the cache matrix using explicit namespaces."""
        qualified = self._qualify_key(key)
        async def _set(redis_inst: Redis) -> Any:
            return await redis_inst.set(qualified, value, ex=expire_seconds)
        return bool(await self._execute_with_retry(_set))

    async def delete(self, key: str) -> bool:
        """Evicts a target descriptor entry directly out of active structural layers."""
        qualified = self._qualify_key(key)
        async def _delete(redis_inst: Redis) -> Any:
            return await redis_inst.delete(qualified)
        return bool(await self._execute_with_retry(_delete))

    async def exists(self, key: str) -> bool:
        """Validates physical structural presence of target identifiers within active memory frames."""
        qualified = self._qualify_key(key)
        async def _exists(redis_inst: Redis) -> Any:
            return await redis_inst.exists(qualified)
        return bool(await self._execute_with_retry(_exists))

    async def increment(self, key: str, increment_by: int = 1) -> int:
        """Atomically steps structural integer trackers forward matching rate limits or sequences."""
        qualified = self._qualify_key(key)
        async def _incr(redis_inst: Redis) -> Any:
            return await redis_inst.incrby(qualified, increment_by)
        return int(await self._execute_with_retry(_incr))

    # --- Complex High-Performance Data Structure Extensions ---

    async def set_hash_field(self, hash_key: str, field: str, value_payload: Any) -> bool:
        """Binds localized properties into multi-tenant dictionary models stored in Redis hashes."""
        qualified = self._qualify_key(hash_key)
        serialized = json.dumps(value_payload)
        async def _hset(redis_inst: Redis) -> Any:
            return await redis_inst.hset(qualified, field, serialized)
        return bool(await self._execute_with_retry(_hset))

    async def get_hash_field(self, hash_key: str, field: str) -> Optional[Any]:
        """Extracts individual parameter rows from target composite dictionary rows securely."""
        qualified = self._qualify_key(hash_key)
        async def _hget(redis_inst: Redis) -> Any:
            val = await redis_inst.hget(qualified, field)
            return json.loads(val.decode("utf-8")) if val else None
        return await self._execute_with_retry(_hget)

    # --- Pub/Sub Messaging Subsystem Implementation ---

    async def publish_message(self, channel_name: str, structured_message: dict[str, Any]) -> int:
        """Pushes event models out onto distribution buses to trigger backend actions.

        Args:
            channel_name: Execution routing destination string identifier.
            structured_message: Dictionary payload compiled into serialized structures.
        """
        qualified_channel = self._qualify_key(channel_name)
        payload_str = json.dumps(structured_message)
        async def _publish(redis_inst: Redis) -> Any:
            return await redis_inst.publish(qualified_channel, payload_str)
        return int(await self._execute_with_retry(_publish))

    async def listen_to_channel(self, channel_name: str) -> AsyncIterator[dict[str, Any]]:
        """Yields clean deserialized payloads systematically from continuous event streams."""
        if not self.client:
            await self.connect()
        
        qualified_channel = self._qualify_key(channel_name)
        pubsub: PubSub = self.client.pubsub()
        await pubsub.subscribe(qualified_channel)
        
        try:
            async for raw_msg in pubsub.listen():
                if raw_msg["type"] == "message":
                    data_bytes = raw_msg["data"]
                    yield json.loads(data_bytes.decode("utf-8"))
        finally:
            await pubsub.unsubscribe(qualified_channel)
            await pubsub.close()
