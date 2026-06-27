# services.py
"""Production-grade Analytics Service.

Encapsulates advanced business intelligence and predictive modeling logic. 
Orchestrates complex data aggregation, cohort analysis, and fraud detection 
pipelines. Provides high-performance executive dashboards and forecasting 
models to support strategic decision-making within the investment platform.
"""

import logging
from typing import Final, Any
from decimal import Decimal

from src.modules.analytics.dtos import ExecutiveSummaryDTO, FraudIndicatorDTO
from src.modules.analytics.exceptions import AnalyticsError

logger = logging.getLogger("investment_platform.modules.analytics.services")


class AnalyticsService:
    """Core domain service for advanced platform analytics and predictive modeling."""

    def __init__(
        self,
        financial_repo: Any,
        user_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._financial_repo: Final = financial_repo
        self._user_repo: Final = user_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_executive_summary(self) -> ExecutiveSummaryDTO:
        """Generates a high-level business intelligence dashboard summary."""
        cache_key = "analytics_executive_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            # Aggregate complex KPIs
            summary = ExecutiveSummaryDTO(
                revenue_growth=await self._financial_repo.calculate_revenue_growth(),
                conversion_rate=await self._user_repo.calculate_conversion_rate(),
                churn_rate=await self._user_repo.calculate_churn_rate()
            )
            
            await self._cache.set(cache_key, summary, ttl=900)
            await self._event_bus.publish("analytics.executive_dashboard_updated", {})
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate executive analytics: {e}")
            raise AnalyticsError("BI dashboard aggregation failure.")

    async def get_fraud_indicators(self) -> list[FraudIndicatorDTO]:
        """Analyzes transaction patterns to identify potential fraud risks."""
        try:
            # Detect anomalous patterns via aggregate analysis
            indicators = await self._financial_repo.detect_anomalies()
            return [FraudIndicatorDTO(**item) for item in indicators]
        except Exception as e:
            logger.error(f"Fraud analysis engine failure: {e}")
            raise AnalyticsError("Fraud intelligence generation failed.")

    async def refresh_analytics(self) -> None:
        """Synchronizes and invalidates all analytical caches."""
        try:
            await self._cache.delete_pattern("analytics_*")
            await self._event_bus.publish("analytics.cache_updated", {})
        except Exception as e:
            logger.error(f"Analytics synchronization error: {e}")
            raise AnalyticsError("Failed to purge analytics caches.")
