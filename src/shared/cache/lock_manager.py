# lock_manager.py
"""Distributed Lock Manager Subsystem.

Provides an enterprise-grade distributed mutual exclusion mechanism utilizing Redis.
Ensures transaction safety across concurrent execution contexts, preventing race
conditions in financial operations (e.g., duplicate withdrawals, compounding accruals)
via atomic script evaluations, ownership tokens, and async context managers.
"""

import asyncio
import logging
import secrets
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Final, Optional

from src.shared.cache.redis_client import RedisCacheClient

logger = logging.getLogger("investment_platform.shared.cache.lock")

# Lua scripts for atomic single-roundtrip execution blocks
LUA_RELEASE_SCRIPT: Final[str] = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""

LUA_EXTEND_SCRIPT: Final[str] = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('pexpire', KEYS[1], ARGV[2])
else
    return 0
end
"""


class LockAcquisitionError(Exception):
    """Raised when a distributed lock cannot be acquired within constraints."""
    pass


class DistributedLock:
    """Active instance handle for an acquired distributed mutual exclusion lock."""

    def __init__(
        self,
        manager: "DistributedLockManager",
        name: str,
        token: str,
        ttl_ms: int
    ) -> None:
        self._manager: Final["DistributedLockManager"] = manager
        self.name: Final[str] = name
        self.token: Final[str] = token
        self.ttl_ms: int = ttl_ms


class DistributedLockManager:
    """Coordinates and governs distributed locks across application instances."""

    def __init__(self, redis_client: RedisCacheClient, prefix_namespace: str = "lock:") -> None:
        """Initializes the lock manager.

        Args:
            redis_client: Active shared network data cache manager proxy.
            prefix_namespace: Enforces explicit key separation from generic caches.
        """
        self.redis_client: Final[RedisCacheClient] = redis_client
        self.namespace: Final[str] = prefix_namespace

    def _qualify_key(self, lock_name: str) -> str:
        """Constructs a scoped storage system lookup string key."""
        return f"{self.namespace}{lock_name}"

    async def acquire(
        self,
        lock_name: str,
        ttl_seconds: int = 30,
        timeout_seconds: int = 10,
        retry_interval_seconds: float = 0.2
    ) -> DistributedLock:
        """Atomically acquires a unique global distributed execution lock block.

        Args:
            lock_name: Explicit business resource identifier path target.
            ttl_seconds: Automatic system expiration safety threshold window.
            timeout_seconds: Maximum total duration spent retrying target states.
            retry_interval_seconds: Base structural delay sleep period between checks.
        """
        qualified_key = self._qualify_key(lock_name)
        ownership_token = secrets.token_urlsafe(24)
        ttl_ms = ttl_seconds * 1000
        
        start_time = asyncio.get_running_loop().time()
        
        while True:
            if not self.redis_client.client:
                await self.redis_client.connect()
                
            try:
                # Execute string mutation with dynamic conditional arguments atomically
                acquired = await self.redis_client.client.set(
                    name=qualified_key,
                    value=ownership_token,
                    px=ttl_ms,
                    nx=True
                )
                if acquired:
                    logger.debug(f"Acquired lock profile context path reference: '{qualified_key}'")
                    return DistributedLock(self, lock_name, ownership_token, ttl_ms)
            except Exception as cluster_fault:
                logger.error(f"Error communicating with Redis cluster lock layers: {cluster_fault}")

            if (asyncio.get_running_loop().time() - start_time) >= timeout_seconds:
                logger.warning(f"SLA Conflict Timeout: Refusing wait constraints for resource path: '{qualified_key}'")
                raise LockAcquisitionError(f"Resource contention boundary lock timeout on target: '{lock_name}'")

            await asyncio.sleep(retry_interval_seconds)

    async def release(self, lock: DistributedLock) -> bool:
        """Safely executes custom tracking scripts to evict tokens if ownership passes.

        Args:
            lock: Active structural authorization parameter entity handle.
        """
        qualified_key = self._qualify_key(lock.name)
        if not self.redis_client.client:
            return False

        try:
            result = await self.redis_client.client.eval(
                LUA_RELEASE_SCRIPT,
                1,
                qualified_key,
                lock.token
            )
            success = bool(result)
            if success:
                logger.debug(f"Distributed lock structure released programmatically: '{qualified_key}'")
            return success
        except Exception as script_fault:
            logger.error(f"Failed to execute atomic remote release sequence script evaluation: {script_fault}")
            return False

    async def extend(self, lock: DistributedLock, extend_ms: int) -> bool:
        """Extends an active lock's lifetime if ownership remains valid."""
        qualified_key = self._qualify_key(lock.name)
        if not self.redis_client.client:
            return False

        try:
            result = await self.redis_client.client.eval(
                LUA_EXTEND_SCRIPT,
                1,
                qualified_key,
                lock.token,
                extend_ms
            )
            success = bool(result)
            if success:
                lock.ttl_ms = extend_ms
                logger.debug(f"Renewed lock allocation bounds for target structure: '{qualified_key}' across {extend_ms}ms")
            return success
        except Exception as script_fault:
            logger.error(f"Failed to execute atomic extension script evaluation: {script_fault}")
            return False

    async def force_unlock(self, lock_name: str) -> None:
        """Bypasses normal authorization checks to clear a resource lock immediately."""
        qualified_key = self._qualify_key(lock_name)
        logger.warning(f"Administrative override active. Forcing deletion of lock structure: '{qualified_key}'")
        await self.redis_client.delete(qualified_key)

    @asynccontextmanager
    async def lock(
        self,
        lock_name: str,
        ttl_seconds: int = 30,
        timeout_seconds: int = 10
    ) -> AsyncIterator[DistributedLock]:
        """Provides an asynchronous runtime boundary enclosing isolated data adjustments safely.

        Args:
            lock_name: Targeted database context tracking reference name.
            ttl_seconds: Internal hard limits handling maximum run allocations.
            timeout_seconds: Total timeline constraint allowed before failing calls.
        """
        active_lock = await self.acquire(lock_name, ttl_seconds, timeout_seconds)
        try:
            yield active_lock
        finally:
            await self.release(active_lock)
