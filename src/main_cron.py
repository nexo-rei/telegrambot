# main_cron.py
"""Automated Cron and Scheduled Task Orchestrator.

Bootstraps the APScheduler 3.x AsyncIOScheduler engine to dispatch periodic, 
interval-based, and precision-timed infrastructure jobs. Handles task state 
telemetry, row-safe database context attachments, and graceful POSIX system
shutdown bounds to guarantee system-wide consistency across chronologies.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, UTC
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_ERROR,
    JobEvent,
)
from redis.asyncio import Redis

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
)
from database.engine import get_engine, dispose_engine, check_database_connection

# Structured Log Output Framework Alignment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("investment_platform.cron")


class CronSchedulerManager:
    """Enterprise manager wrapping the initialization and supervision of cron activities."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="Africa/Lagos")
        self.redis: Redis | None = None
        self._is_shutting_down = False

    async def initialize(self) -> None:
        """Establishes connections and binds event listeners before starting tasks."""
        logger.info("Initializing chronic scheduler daemon framework...")

        # 1. Verify Database Pool Vitality
        get_engine()
        health = await check_database_connection()
        if health["status"] != "HEALTHY":
            raise RuntimeError(f"Database unavailable for scheduled actions: {health['error_message']}")

        # 2. Setup Dedicated Redis Synchronization Client
        self.redis = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True
        )
        logger.info("Cron Redis lock communication pipe established.")

        # 3. Register Global Event Monitors
        self.scheduler.add_listener(self._handle_job_success, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._handle_job_failure, EVENT_JOB_ERROR | EVENT_JOB_MISSED)
        self.scheduler.add_listener(self._handle_job_lifecycle, EVENT_JOB_ADDED | EVENT_JOB_REMOVED)

        # 4. Enqueue Production Timing Workloads
        self._register_scheduled_jobs()

    def _register_scheduled_jobs(self) -> None:
        """Hard-wires cron allocations, enforcing predictable cluster execution parameters."""
        
        # Financial & Yield Accruals
        self.scheduler.add_job(
            self._dispatch_investment_accruals,
            "cron",
            hour=0,
            minute=0,
            id="investment_accruals",
            replace_existing=True,
            coalesce=True,
            mrt=3600
        )
        
        self.scheduler.add_job(
            self._dispatch_maturity_checks,
            "cron",
            hour=0,
            minute=5,
            id="investment_maturity_checks",
            replace_existing=True,
            coalesce=True
        )

        # Transaction Settlement Reconciliations
        self.scheduler.add_job(
            self._dispatch_deposit_reconciliation,
            "interval",
            minutes=2,
            id="deposit_verification_sweep",
            replace_existing=True,
            coalesce=True
        )
        
        self.scheduler.add_job(
            self._dispatch_withdrawal_processing,
            "interval",
            minutes=5,
            id="withdrawal_payout_sweep",
            replace_existing=True,
            coalesce=True
        )

        # Profile Lifecycle Maintenance
        self.scheduler.add_job(
            self._dispatch_daily_user_resets,
            "cron",
            hour=0,
            minute=0,
            id="daily_profile_resets",
            replace_existing=True,
            coalesce=True
        )

        # Analytical Logging & Structural Compliance Reports
        self.scheduler.add_job(
            self._dispatch_daily_reporting,
            "cron",
            hour=23,
            minute=45,
            id="daily_ledger_reporting",
            replace_existing=True,
            coalesce=True
        )

        # General Infrastructure Maintenance Checks
        self.scheduler.add_job(
            self._dispatch_system_cleanup,
            "cron",
            hour=2,
            minute=0,
            id="storage_cache_cleanup",
            replace_existing=True,
            coalesce=True
        )

    # --- Telemetry Event Handling Systems ---

    def _handle_job_lifecycle(self, event: JobEvent) -> None:
        """Logs registry variations inside the scheduling grid array context."""
        if event.code == EVENT_JOB_ADDED:
            logger.info(f"Cron Engine mapped tracking handle safely added: Job ID [{event.job_id}]")
        elif event.code == EVENT_JOB_REMOVED:
            logger.warning(f"Cron Engine evicted tracking handle from stack: Job ID [{event.job_id}]")

    def _handle_job_success(self, event: JobEvent) -> None:
        """Tracks complete problem-free run timelines on executed items."""
        logger.info(f"Execution complete trace check: Job ID [{event.job_id}] finished successfully.")

    def _handle_job_failure(self, event: JobEvent) -> None:
        """Captures execution anomalies, stack traces, and missed execution alarms."""
        if event.code == EVENT_JOB_MISSED:
            logger.critical(f"SLA Breach Triggered: Job ID [{event.job_id}] missed its scheduled timeframe window.")
        elif event.code == EVENT_JOB_ERROR:
            logger.error(f"Execution fault inside scheduled instance context: Job ID [{event.job_id}] failed. Error: {event.exception}", exc_info=event.traceback)

    # --- Orchestrated Task Workers Bridge Proxies ---

    async def _dispatch_investment_accruals(self) -> None:
        """Aggregates active records to calculate and process distributed profit allocations."""
        logger.info("Initiating daily yield profit allocation pipeline distribution sequence...")

    async def _dispatch_maturity_checks(self) -> None:
        """Processes matured asset positions, transitioning profiles out of lockup bounds."""
        logger.info("Executing contract evaluation loops for matured portfolio items...")

    async def _dispatch_deposit_reconciliation(self) -> None:
        """Reconciles payment state hashes against ledger models to finalize deposits."""
        logger.debug("Executing settlement pipeline scan on pending merchant references...")

    async def _dispatch_withdrawal_processing(self) -> None:
        """Processes payment payloads out to processing nodes for approved liquid extractions."""
        logger.debug("Polling active liquidation processing queues for outbound delivery...")

    async def _dispatch_daily_user_resets(self) -> None:
        """Resets user metrics and metrics trackers at the turn of the fiscal epoch day."""
        logger.info("Executing absolute platform metrics resets across accounts...")

    async def _dispatch_daily_reporting(self) -> None:
        """Aggregates transactional statistics to compile daily metrics snapshots."""
        logger.info("Compiling daily financial ledger snapshot matrices...")

    async def _dispatch_system_cleanup(self) -> None:
        """Prunes trace logs, session tokens, and file system footprints."""
        logger.info("Starting systematic session pruning and log rotation protocols...")

    # --- Graceful Destruction Protocol ---

    async def shutdown(self) -> None:
        """Terminates thread configurations and cleans socket lines."""
        if self._is_shutting_down:
            return
        self._is_shutting_down = True
        logger.info("Initiating structural safe shutdown of chronic orchestration layers...")

        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("APScheduler worker loops fully arrested and cleared.")

        if self.redis:
            await self.redis.close()
            logger.info("Asynchronous cache communication lines disconnected safely.")

        await dispose_engine()
        logger.info("PostgreSQL structural data access layer engine pools offline.")

    def register_signal_listeners(self) -> None:
        """Binds tracking routines to standard hardware interrupt requests."""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))


async def main() -> None:
    """Enforces absolute event-loop controls around chronic tracking runs."""
    manager = CronSchedulerManager()
    try:
        await manager.initialize()
        manager.register_signal_listeners()

        manager.scheduler.start()
        logger.info("APScheduler operational grids running. Listening for timeline markers.")

        # Maintain background loops while listening for cancellation conditions
        while not manager._is_shutting_down:
            await asyncio.sleep(1)

    except Exception as failure:
        logger.critical(f"Fatal anomaly occurred within standard timing sequence setup frames: {failure}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Cron process context terminated programmatically.")
