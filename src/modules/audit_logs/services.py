# services.py
"""Production-grade Audit Log Service.

Encapsulates business logic for immutable compliance tracking, high-privilege 
administrative action logging, and secure financial audit trails. Orchestrates 
the ingestion, verification, and structured retrieval of sensitive system 
events to meet enterprise regulatory requirements within the investment platform.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.audit_logs.dtos import AuditEntryDTO, AuditStatsDTO
from src.modules.audit_logs.exceptions import AuditProcessingError

logger = logging.getLogger("investment_platform.modules.audit_logs.services")


class AuditLogService:
    """Core domain service for immutable audit trail management and compliance."""

    def __init__(
        self,
        audit_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._repo: Final = audit_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def record_audit_event(
        self,
        actor_id: int,
        action: str,
        category: str,
        target_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> bool:
        """Persists an immutable audit record for sensitive operations."""
        try:
            entry = AuditEntryDTO(
                timestamp=datetime.now(),
                actor_id=actor_id,
                action=action,
                category=category,
                target_id=target_id,
                details=details or {}
            )
            
            success = await self._repo.save(entry)
            if success:
                await self._event_bus.publish("audit.event_recorded", {"category": category})
            return success
            
        except Exception as e:
            logger.error(f"Failed to record audit event for {actor_id}: {e}")
            raise AuditProcessingError("Audit persistence failure.")

    async def get_audit_entries(self, category: str, limit: int = 20) -> list[AuditEntryDTO]:
        """Retrieves categorized audit records using a high-performance cache-first strategy."""
        cache_key = f"audit_trail_{category}_{limit}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            entries = await self._repo.fetch_entries(category, limit)
            await self._cache.set(cache_key, entries, ttl=60)
            return entries
        except Exception as e:
            logger.error(f"Error fetching audit records for {category}: {e}")
            raise AuditProcessingError("Retrieval failure.")

    async def get_audit_statistics(self) -> AuditStatsDTO:
        """Calculates current audit trail volume and compliance metrics."""
        cache_key = "audit_stats_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            stats = await self._repo.get_aggregate_stats()
            await self._cache.set(cache_key, stats, ttl=300)
            return stats
        except Exception as e:
            logger.error(f"Audit statistics calculation error: {e}")
            raise AuditProcessingError("Statistical aggregation failed.")
