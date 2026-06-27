# celery_broker.py
"""Enterprise-Grade Celery Broker Configuration.

Provides the foundational infrastructure for distributed task execution. Configures 
the Celery application, task routing, serialization, and high-availability 
connections to the Redis backend. Ensures reliable background processing for 
financial transactions, notifications, and scheduled cron jobs.
"""

import logging
from typing import Final

from celery import Celery
from kombu import Queue, Exchange

logger = logging.getLogger("investment_platform.shared.queue_manager")

# Application Constants
CELERY_APP_NAME: Final[str] = "investment_platform_worker"
BROKER_URL: Final[str] = "redis://localhost:6379/0"
BACKEND_URL: Final[str] = "redis://localhost:6379/1"

# Celery Application Initialization
celery_app = Celery(CELERY_APP_NAME, broker=BROKER_URL, backend=BACKEND_URL)

# Task Routing Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("payments", Exchange("payments"), routing_key="payments"),
        Queue("investments", Exchange("investments"), routing_key="investments"),
        Queue("notifications", Exchange("notifications"), routing_key="notifications"),
        Queue("scheduler", Exchange("scheduler"), routing_key="scheduler"),
    ),
    task_routes={
        "tasks.payments.*": {"queue": "payments"},
        "tasks.investments.*": {"queue": "investments"},
        "tasks.notifications.*": {"queue": "notifications"},
        "tasks.scheduler.*": {"queue": "scheduler"},
    },
)


class CeleryBroker:
    """Production-grade broker interface for asynchronous task dispatch."""

    def __init__(self, app: Celery = celery_app) -> None:
        self._app = app

    def dispatch(self, task_name: str, *args: Any, **kwargs: Any) -> Any:
        """Dispatches a task to the asynchronous worker pool."""
        try:
            return self._app.send_task(task_name, args=args, kwargs=kwargs)
        except Exception as e:
            logger.error(f"Task dispatch failure for {task_name}: {e}")
            raise

    @property
    def is_connected(self) -> bool:
        """Validates connection status with the Redis broker."""
        try:
            return self._app.broker_connection().connected
        except Exception:
            return False

    def get_queue_stats(self, queue_name: str) -> int:
        """Returns the pending task count for the specified queue."""
        with self._app.connection_or_acquire() as conn:
            return conn.default_channel.queue_declare(
                queue=queue_name, passive=True
            ).message_count
