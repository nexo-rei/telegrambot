# services.py
"""Production-grade Scheduler Service.

Encapsulates business logic for distributed task orchestration and background 
job management. Orchestrates recurring financial distributions, system 
maintenance, and analytical reporting workflows. Integrates with distributed 
locking mechanisms and persistent backends to ensure atomic task execution 
across the enterprise investment platform.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.scheduler.dtos import JobStatusDTO, SchedulerHealthDTO
from src.modules.scheduler.exceptions import SchedulerError

logger = logging.getLogger("investment_platform.modules.scheduler.services")


class SchedulerService:
    """Core domain service for background job orchestration and worker monitoring."""

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

    async def get_scheduler_health(self) -> SchedulerHealthDTO:
        """Retrieves real-time operational status of the scheduler worker."""
        cache_key = "scheduler_health_status"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            health = SchedulerHealthDTO(
                is_running=self._engine.running,
                active_job_count=len(self._engine.get_jobs()),
                failed_job_count=await self._engine.get_failed_count()
            )
            
            await self._cache.set(cache_key, health, ttl=30)
            return health
        except Exception as e:
            logger.error(f"Scheduler health check failure: {e}")
            raise SchedulerError("Unable to retrieve scheduler diagnostics.")

    async def get_scheduled_jobs(self) -> list[JobStatusDTO]:
        """Lists all registered persistent tasks and their execution schedules."""
        try:
            jobs = self._engine.get_jobs()
            return [
                JobStatusDTO(
                    name=job.name,
                    next_run=job.next_run_time,
                    status="scheduled"
                ) for job in jobs
            ]
        except Exception as e:
            logger.error(f"Failed to fetch job registry: {e}")
            raise SchedulerError("Job enumeration failed.")

    async def pause_job(self, job_id: str) -> bool:
        """Temporarily suspends a scheduled task using distributed locking."""
        async with self._locks.acquire(f"lock:job:{job_id}"):
            try:
                self._engine.pause_job(job_id)
                await self._event_bus.publish("scheduler.job_cancelled", {"job_id": job_id})
                await self._cache.delete("scheduler_health_status")
                return True
            except Exception as e:
                logger.error(f"Failed to pause job {job_id}: {e}")
                raise SchedulerError(f"Job suspension error for {job_id}.")
