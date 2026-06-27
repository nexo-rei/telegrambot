# maintenance.py
"""Enterprise System Maintenance Governance Middleware.

Provides a global kill-switch for platform operations. When active, this middleware 
prevents non-authorized users from interacting with the bot while allowing 
administrative personnel to perform deployments, database migrations, or emergency 
repairs. Utilizes high-performance Redis state lookups to ensure near-instantaneous 
broadcast of maintenance status across all distributed instances.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Final, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.exceptions import RedisError

from src.shared.cache.redis_client import RedisCacheClient
from src.shared.constants.system import REDIS_NAMESPACE_PREFIX

logger = logging.getLogger("investment_platform.shared.middleware.maintenance")

# Maintenance Configuration Keys
MAINTENANCE_KEY: Final[str] = "status:global_maintenance"
MAINTENANCE_MESSAGE: Final[str] = (
    "<b>⚠️ System Maintenance in Progress</b>\n\n"
    "We are currently performing essential system upgrades to improve "
    "your investment experience. Access is temporarily restricted.\n\n"
    "Please check back shortly."
)


class MaintenanceMiddleware(BaseMiddleware):
    """Production-grade middleware to gate platform access during maintenance windows."""

    def __init__(self) -> None:
        """Initializes the maintenance control gateway with Redis backing."""
        self._cache = RedisCacheClient(prefix_namespace=f"{REDIS_NAMESPACE_PREFIX}system:")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Intercepts requests to evaluate if the system is in a restricted state."""
        # Administrative bypass: Admins and SuperAdmins always retain access
        user_role = data.get("user_role", "GUEST")
        if user_role in ("ADMIN", "SUPERADMIN"):
            return await handler(event, data)

        try:
            is_maintenance = await self._cache.get(MAINTENANCE_KEY)
            
            if is_maintenance:
                user: Optional[User] = data.get("event_from_user")
                logger.info(
                    f"Blocked access request from UID {user.id if user else 'Unknown'} "
                    "due to active maintenance mode."
                )
                
                # Logic for notifying the user of the outage
                if hasattr(event, "answer"):
                    await event.answer(MAINTENANCE_MESSAGE, parse_mode="HTML")
                
                return None  # Halt handler execution chain

        except RedisError as fault:
            logger.error(f"Maintenance status cache lookup failure: {fault}")
            # Fail-safe: In the event of cache failure, we allow access to avoid 
            # locking out legitimate users during system instability.

        return await handler(event, data)
