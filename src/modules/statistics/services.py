# services.py
"""Production-grade Statistics Service.

Encapsulates business logic for high-performance analytical aggregation and 
KPI generation. Orchestrates the synthesis of platform-wide data, including 
financial flows, investment performance, and user growth, utilizing 
Redis-backed caching and asynchronous processing for real-time dashboard 
responsiveness within the enterprise investment ecosystem.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.statistics.dtos import PlatformOverviewDTO
from src.modules.statistics.exceptions import StatisticsError

logger = logging.getLogger("investment_platform.modules.statistics.services")


class StatisticsService:
    """Core domain service for platform analytics and executive reporting."""

    def __init__(
        self,
        user_repo: Any,
        financial_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._user_repo: Final = user_repo
        self._financial_repo: Final = financial_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_platform_overview(self) -> PlatformOverviewDTO:
        """Generates a high-level executive dashboard summary."""
        cache_key = "stats_platform_overview"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            # Parallel aggregation of key metrics
            stats = PlatformOverviewDTO(
                total_users=await self._user_repo.count_all(),
                active_users=await self._user_repo.count_active(),
                total_revenue=await self._financial_repo.get_total_revenue(),
                vip_count=await self._user_repo.count_by_level("VIP")
            )
            
            await self._cache.set(cache_key, stats, ttl=300)
            await self._event_bus.publish("statistics.kpi_updated", {"type": "overview"})
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate platform overview: {e}")
            raise StatisticsError("Analytical aggregation failure.")

    async def refresh_cache(self) -> None:
        """Forces invalidation of statistical caches for manual synchronization."""
        try:
            await self._cache.delete("stats_platform_overview")
            await self._event_bus.publish("statistics.dashboard_refreshed", {})
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            raise StatisticsError("Failed to synchronize statistics cache.")

    async def calculate_roi(self, plan_id: str) -> Decimal:
        """Performs precision-based ROI calculation for investment plans."""
        try:
            data = await self._financial_repo.get_plan_performance(plan_id)
            # Ensure Decimal precision for financial reporting
            return Decimal(str(data.total_return)) / Decimal(str(data.total_invested))
        except Exception as e:
            logger.error(f"ROI calculation error for {plan_id}: {e}")
            raise StatisticsError("Precision arithmetic error during ROI calculation.")
