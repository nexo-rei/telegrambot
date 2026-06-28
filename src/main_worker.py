# main_worker.py
"""Background Worker Entry Point.

Orchestrates the Celery 5.x application lifecycle, configures the Redis broker
and result backend, establishes database engine hooks, and ensures auto-discovery
of critical platform task modules for asynchronous and scheduled execution.

BUG FIXES:
  - `dispose_engine()` is an async function but was called without `await` in the
    worker_shutdown signal handler. Celery signal handlers are synchronous, so we
    must use asyncio.run() to call it correctly.
  - `REDIS_URL` and `DATABASE_URL` were imported from `config` but were not exported
    there (fixed in config/__init__.py).
  - Celery autodiscover references `src.tasks.*` modules that don't exist; removed
    the autodiscover call to prevent ImportError on startup.
"""

import asyncio
import logging
import sys
from typing import Any

from celery import Celery
from celery.signals import worker_init, worker_ready, worker_shutdown

from config import REDIS_URL
from database.engine import get_engine, dispose_engine

# Structured Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("investment_platform.worker")

# Initialize and Configure Celery Enterprise Application Instance
celery_app = Celery(
    "investment_platform_workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Production Optimization Tuning Parameters
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
    worker_prefetch_multiplier=1,   # Prevent task hoarding for uneven workloads
    task_acks_late=True,            # Ensure idempotent tasks are acknowledged post-execution
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_expires=86400,           # Prune task records after 24 hours
)

# BUG FIX: Original called autodiscover_tasks for `src.tasks.*` modules which do not
# exist in this project, causing an ImportError on worker startup. Removed.
# Task modules should be imported explicitly when they are created.


@worker_init.connect
def bootstrap_worker_infrastructure(**kwargs: Any) -> None:
    """Fires immediately when the worker process boots up."""
    logger.info("Bootstrapping worker infrastructure context pools...")
    try:
        get_engine()
        logger.info("PostgreSQL engine initialization completed inside worker pool scope.")
    except Exception as error:
        logger.critical(
            f"Fatal exception during worker infrastructure pool bootstrap: {error}", exc_info=True
        )
        sys.exit(1)


@worker_ready.connect
def worker_readiness_notification(sender: Any, **kwargs: Any) -> None:
    """Fires once the consumer loop is active and listening to the broker streams."""
    logger.info(
        f"Celery worker node '{sender.hostname}' is fully synchronized and ready to accept tasks."
    )


@worker_shutdown.connect
def graceful_worker_teardown(**kwargs: Any) -> None:
    """Fires before the process terminates under standard system teardown signals.

    BUG FIX: dispose_engine() is an async coroutine but was called without await.
    Celery signal handlers are synchronous, so asyncio.run() is required.
    """
    logger.info(
        "SIGINT/SIGTERM intercepted. Initiating graceful teardown of worker connections..."
    )
    try:
        # BUG FIX: Must use asyncio.run() since this is a sync signal handler
        asyncio.run(dispose_engine())
        logger.info("PostgreSQL connection pools successfully drained inside worker context.")
    except Exception as error:
        logger.error(
            f"Error encountered during connection pool termination sequence: {error}", exc_info=True
        )
