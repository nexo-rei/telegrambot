# services.py
"""Production-grade Fraud Security Service.

Encapsulates business logic for automated threat detection, risk assessment, 
and defensive security orchestration. Utilizes multi-factor heuristic analysis 
to identify account abuse, referral fraud, and suspicious transactional 
behavior while maintaining high-performance state tracking via Redis.
"""

import logging
from typing import Final, Any, Optional
from decimal import Decimal

from src.modules.fraud_security.dtos import FraudStatsDTO, ActivityRecordDTO
from src.modules.fraud_security.exceptions import FraudSecurityError

logger = logging.getLogger("investment_platform.modules.fraud_security.services")


class FraudSecurityService:
    """Core domain service for enterprise fraud detection and risk management."""

    def __init__(
        self,
        risk_engine: Any,
        cache_manager: Any,
        event_bus: Any,
        repository: Any
    ) -> None:
        self._risk_engine: Final = risk_engine
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._repo: Final = repository

    async def get_fraud_statistics(self) -> FraudStatsDTO:
        """Aggregates system-wide fraud health metrics and threat landscape data."""
        cache_key = "fraud_stats_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            stats = await self._repo.get_aggregate_risk_metrics()
            await self._cache.set(cache_key, stats, ttl=300)
            return stats
        except Exception as e:
            logger.error(f"Fraud statistics aggregation failure: {e}")
            raise FraudSecurityError("Unable to retrieve fraud security metrics.")

    async def analyze_user_risk(self, user_id: int) -> Decimal:
        """Calculates a weighted risk score based on behavioral heuristics and audit logs."""
        try:
            # Aggregate data points for risk evaluation
            user_data = await self._repo.get_user_security_profile(user_id)
            score = await self._risk_engine.calculate(user_data)
            
            # Cache the result to minimize redundant computational load
            await self._cache.set(f"risk_score:{user_id}", score, ttl=600)
            
            if score > Decimal("0.80"):
                await self._event_bus.publish("security.risk_threshold_exceeded", {"user_id": user_id})
                
            return score
        except Exception as e:
            logger.error(f"Risk analysis error for user {user_id}: {e}")
            raise FraudSecurityError("Failed to calculate user risk score.")

    async def get_suspicious_activities(self) -> list[ActivityRecordDTO]:
        """Retrieves the list of high-risk events requiring administrative review."""
        try:
            return await self._repo.get_recent_flagged_activities(limit=50)
        except Exception as e:
            logger.error(f"Suspicious activity retrieval failure: {e}")
            raise FraudSecurityError("Could not fetch security activity logs.")
