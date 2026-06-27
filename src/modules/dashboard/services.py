# services.py
"""Production-grade Dashboard Service.

Encapsulates all business logic for aggregating financial data, investment 
performance, and user insights. Implements a cache-first strategy using Redis to 
ensure sub-millisecond latency for dashboard delivery, while maintaining 
ACID-consistent data retrieval from the PostgreSQL persistence layer.
"""

import logging
import asyncio
from typing import Final, Any
from decimal import Decimal

from src.modules.dashboard.dtos import DashboardSummaryDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.dashboard.services")


class DashboardService:
    """Core domain service for orchestrating dashboard data aggregation."""

    def __init__(
        self,
        user_repo: Any,
        wallet_repo: Any,
        investment_repo: Any,
        referral_repo: Any,
        cache_manager: Any
    ) -> None:
        self._user_repo: Final = user_repo
        self._wallet_repo: Final = wallet_repo
        self._investment_repo: Final = investment_repo
        self._referral_repo: Final = referral_repo
        self._cache: Final = cache_manager

    async def get_user_summary(self, user_id: int) -> DashboardSummaryDTO:
        """
        Retrieves a consolidated user dashboard summary.
        Uses a cache-first approach to optimize performance.
        """
        cache_key = f"dashboard_summary:{user_id}"
        cached_data = await self._cache.get(cache_key)

        if cached_data:
            return DashboardSummaryDTO(**cached_data)

        # Aggregate data concurrently to minimize latency
        tasks = [
            self._wallet_repo.get_balance(user_id),
            self._investment_repo.get_active_count(user_id),
            self._investment_repo.get_daily_earnings(user_id),
            self._referral_repo.get_earnings(user_id),
            self._user_repo.get_vip_level(user_id)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Basic error handling for aggregation failures
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Dashboard aggregation failed for user {user_id}: {result}")
                raise RuntimeError("Failed to build dashboard summary.")

        summary = DashboardSummaryDTO(
            balance=PrecisionMath.safe_decimal(results[0]),
            active_investments=int(results[1]),
            daily_earnings=PrecisionMath.safe_decimal(results[2]),
            referral_earnings=PrecisionMath.safe_decimal(results[3]),
            vip_level=int(results[4])
        )

        # Update cache with short TTL (e.g., 60 seconds)
        await self._cache.set(cache_key, summary.__dict__, ttl=60)
        
        return summary

    async def invalidate_cache(self, user_id: int) -> None:
        """Forces a dashboard refresh by clearing the user's cache entry."""
        await self._cache.delete(f"dashboard_summary:{user_id}")
        logger.debug(f"Dashboard cache invalidated for user {user_id}")
