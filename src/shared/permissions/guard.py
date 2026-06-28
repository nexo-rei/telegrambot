# guard.py
"""Centralized Role-Based Access Control (RBAC) Guard.

BUG FIX: `self._cache.set(cache_key, [s.value for s in scopes], ...)` passes a
Python list as the value, but RedisCacheClient.set() expects a `str`. This would
cause a TypeError at runtime. Fixed by JSON-serializing the list before storing
and deserializing on retrieval.
"""

import json
import logging
from typing import Final, Sequence, Union

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX
from src.shared.permissions.scopes import PermissionScope

logger = logging.getLogger("investment_platform.shared.permissions.guard")

# Permission cache TTL (5 minutes) for rapid validation
PERMISSION_CACHE_TTL: Final[int] = 300


class PermissionDenied(Exception):
    """Exception raised when an authenticated user lacks sufficient privileges."""
    pass


class PermissionGuard:
    """Production-grade authorization engine for role and scope verification."""

    def __init__(self) -> None:
        """Initializes the guard with distributed Redis-backed scope caching."""
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}rbac:")

    async def has_permission(
        self,
        user_id: int,
        required_permissions: Union[PermissionScope, Sequence[PermissionScope]],
        match_all: bool = True,
    ) -> bool:
        """Evaluates if the user possesses the necessary scope to perform an operation."""
        user_scopes = await self._get_user_scopes(user_id)

        if isinstance(required_permissions, PermissionScope):
            required_permissions = [required_permissions]

        if match_all:
            return all(p in user_scopes for p in required_permissions)

        return any(p in user_scopes for p in required_permissions)

    async def _get_user_scopes(self, user_id: int) -> set[PermissionScope]:
        """Resolves the authorized permission set via cache-first strategy."""
        cache_key = f"scopes:{user_id}"

        # Cache lookup
        cached_scopes_str = await self._cache.get(cache_key)
        if cached_scopes_str:
            try:
                # BUG FIX: Deserialize JSON string back to a list of scope values
                scope_values = json.loads(cached_scopes_str)
                return {PermissionScope(s) for s in scope_values}
            except (json.JSONDecodeError, ValueError):
                pass

        # Repository fallback (Integration point: Load from database)
        scopes: set[PermissionScope] = set()

        # BUG FIX: Serialize the list to JSON string before storing in Redis
        await self._cache.set(
            cache_key,
            json.dumps([s.value for s in scopes]),
            expire_seconds=PERMISSION_CACHE_TTL,
        )
        return scopes

    async def verify_or_raise(
        self,
        user_id: int,
        permission: PermissionScope,
        error_message: str = "Access denied.",
    ) -> None:
        """Verification wrapper that raises an exception on unauthorized access."""
        if not await self.has_permission(user_id, permission):
            logger.warning(
                f"Authorization failure: UID {user_id} attempted unauthorized {permission.value}"
            )
            raise PermissionDenied(error_message)
