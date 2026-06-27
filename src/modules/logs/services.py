# services.py
"""Production-grade Log Service.

Encapsulates business logic for centralized telemetry, audit trail maintenance, 
and operational diagnostics. Orchestrates the ingestion, persistence, and 
structured retrieval of system events across financial, security, and 
application domains within the investment platform.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.logs.dtos import LogEntryDTO
from src.modules.logs.exceptions import LogProcessingError

logger = logging.getLogger("investment_platform.modules.logs.services")


class LogService:
    """Core domain service for structured system telemetry and audit logging."""

    def __init__(
        self,
        log_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._repo: Final = log_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def record_event(
        self, 
        category: str, 
        level: str, 
        message: str, 
        user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Persists a structured log event with user and correlation context."""
        try:
            entry = LogEntryDTO(
                timestamp=datetime.now(),
                category=category,
                level=level,
                message=message,
                user_id=user_id,
                correlation_id=correlation_id
            )
            
            success = await self._repo.save(entry)
            if success:
                await self._event_bus.publish("logs.log_created", {"category": category})
            return success
            
        except Exception as e:
            logger.error(f"Persistence error for log event: {e}")
            raise LogProcessingError("Failed to record system event.")

    async def get_recent_logs(self, category: str, limit: int = 20) -> list[LogEntryDTO]:
        """Retrieves categorized logs, utilizing a cache-first retrieval strategy."""
        cache_key = f"logs_recent_{category}_{limit}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            logs = await self._repo.fetch_recent(category, limit)
            await self._cache.set(cache_key, logs, ttl=30)
            return logs
        except Exception as e:
            logger.error(f"Error fetching logs for category {category}: {e}")
            raise LogProcessingError("Log retrieval failure.")

    async def generate_volume_statistics(self) -> dict[str, int]:
        """Aggregates log volume metrics for system health reporting."""
        try:
            return await self._repo.get_aggregate_counts()
        except Exception as e:
            logger.error(f"Failed to generate log statistics: {e}")
            raise LogProcessingError("Statistical aggregation failed.")
