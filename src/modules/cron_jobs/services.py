# services.py
"""Production-grade Cron Job Service.

Encapsulates business logic for declarative time-triggered task orchestration. 
Manages the lifecycle of recurring operations—from financial reconciliation to 
automated maintenance—integrating with distributed locking and Redis-backed 
state persistence to ensure reliable, atomic execution across the investment 
platform infrastructure.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.cron_jobs.dtos import CronStatsDTO, CronJobEntryDTO
from src.modules.cron_jobs.exceptions import CronJobError

logger = logging.getLogger("investment_platform.modules.cron_jobs.services")


class CronJobService:
    """Core domain service for cron-based background task orchestration."""

    def __init__(
        self,
        scheduler_engine: Any,
        cache_manager: Any,
        event_bus: Any,
        lock_manager: Any
    ) -> None:
        self._engine: Final = scheduler_engine
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._locks: Final = lock_manager

    async def get_cron_statistics(self) -> CronStatsDTO:
        """Aggregates real-time health and execution statistics for the cron registry."""
        cache_key = "cron_job_stats_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            stats = CronStatsDTO(
                active_count=await self._engine.get_active_count(),
                disabled_count=await self._engine.get_disabled_count(),
                failure_count=await self._engine.get_failure_count()
            )
            
            await self._cache.set(cache_key, stats, ttl=60)
            return stats
        except Exception as e:
            logger.error(f"Cron statistics aggregation error: {e}")
            raise CronJobError("Failed to generate cron operational metrics.")

    async def trigger_manual_execution(self, job_id: str) -> bool:
        """Manually invokes a registered cron job utilizing distributed locking to prevent overlap."""
        lock_key = f"cron_lock:{job_id}"
        
        async with self._locks.acquire(lock_key, timeout=10):
            try:
                success = await self._engine.execute_job(job_id)
                if success:
                    await self._event_bus.publish("cron_jobs.job_started", {"job_id": job_id})
                return success
            except Exception as e:
                logger.error(f"Manual trigger failure for {job_id}: {e}")
                raise CronJobError(f"Execution failed for job: {job_id}")

    async def toggle_cron_job(self, job_id: str, enabled: bool) -> bool:
        """Updates the operational state of a cron job and invalidates dependent caches."""
        try:
            status = await self._engine.set_enabled_state(job_id, enabled)
            if status:
                await self._cache.delete("cron_job_stats_summary")
                event_type = "cron_jobs.job_enabled" if enabled else "cron_jobs.job_disabled"
                await self._event_bus.publish(event_type, {"job_id": job_id})
            return status
        except Exception as e:
            logger.error(f"State transition failure for {job_id}: {e}")
            raise CronJobError(f"Could not {'enable' if enabled else 'disable'} job.")
