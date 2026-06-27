# main_bot.py
"""Application Bootstrap Entry Point.

Orchestrates the asynchronous startup initialization sequence, event routing
matrices, middleware pipelines, infrastructure hook mappings (PostgreSQL, Redis),
background job loops, and safe POSIX termination protocols for the application.
"""

from typing import Any
import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from src.modules.authentication.handlers import router as auth_router

# Configuration Component Registries
from config import (
    BOT_TOKEN,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    MAINTENANCE_MODE,
)

# Core Infrastructure Layers
from database.engine import get_engine, dispose_engine, check_database_connection

# TODO/Stubs placeholder exclusion tracking: Explicit architectural setup imports
# Assuming standard layout paths for the application infrastructure
# from src.routers import get_root_router
# from src.middlewares import register_global_middlewares
# from src.scheduler import start_scheduler, stop_scheduler

# Unified Production Logging Schema Mapping
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("investment_platform.bootstrap")


class ApplicationLifecycleManager:
    """Manages the startup, running execution loops, and graceful teardown of the bot."""

    def __init__(self) -> None:
        self.bot: Bot | None = None
        self.dispatcher: Dispatcher | None = None
        self.redis: Redis | None = None
        self.storage: RedisStorage | None = None
        self._is_shutting_down: bool = False

    async def initialize(self) -> None:
        """Bootstraps upstream dependencies and establishes persistent operational scopes."""
        logger.info("Initializing enterprise bot runtime kernel...")

        # 1. Verify Absolute Database State Integration
        try:
            get_engine()
            health_check = await check_database_connection()
            if health_check["status"] != "HEALTHY":
                raise RuntimeError(f"Database health state verification failed: {health_check['error_message']}")
            logger.info("Database connection layer verified and stable.")
        except Exception as error:
            logger.critical("Subsystem bootstrap sequence aborted. Database layer down.", exc_info=True)
            raise error

        # 2. Asynchronous Redis Driver Setup for FSM & Token Buffers
        try:
            self.redis = Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=False,  # Enforce binary payload compatibility for aiogram FSM serialization
            )
            self.storage = RedisStorage(redis=self.redis)
            logger.info("Asynchronous Redis storage adapter connected successfully.")
        except Exception as error:
            logger.critical("Subsystem bootstrap sequence aborted. Cache layer down.", exc_info=True)
            raise error

        # 3. Create Upstream Core Bot Engine Instance Layouts
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # 4. Instantiate Central Event Demultiplexer Dispatcher Context
        self.dispatcher = Dispatcher(storage=self.storage)
        self.dispatcher.include_router(auth_router)

        # 5. Connect Dynamic Runtime State Infrastructure Triggers
        self.dispatcher.startup.register(self._on_startup_event)
        self.dispatcher.shutdown.register(self._on_shutdown_event)

        # 6. Global Exception Interception Core Routing Layout
        @self.dispatcher.errors()
        async def global_error_handler(event: Any) -> bool:
            logger.error(f"Unhandled operational exception intercepted: {event.exception}", exc_info=True)
            return True

        if MAINTENANCE_MODE:
            logger.warning("[WARNING] System is currently flagged as running in MAINTENANCE MODE.")

    async def _on_startup_event(self, bot: Bot) -> None:
        """Asynchronous execution bridge executing specialized task sequences post-binding."""
        logger.info("Executing runtime subsystem mapping sequences...")
        
        # [Enterprise Router & Middleware Registrations Bind Hierarchies Here]
        # Example: self.dispatcher.include_router(get_root_router())
        # Example: register_global_middlewares(self.dispatcher)
        
        # [Initialize Background Cron Engine / Schedulers Here]
        # Example: await start_scheduler()
        
        logger.info("Subsystem execution routing maps locked. Bot listening parameters active.")

    async def _on_shutdown_event(self, bot: Bot) -> None:
        """Asynchronous execution bridge executing automated connection flushing events safely."""
        logger.info("Executing runtime subsystem cleanup sequences...")
        
        # [Stop Background Cron Engine / Schedulers Explicitly]
        # Example: await stop_scheduler()

    async def shutdown(self) -> None:
        """Gracefully flushes open stream arrays and cuts physical sockets without leaks."""
        if self._is_shutting_down:
            return
        
        self._is_shutting_down = True
        logger.info("SIGINT/SIGTERM received. Starting graceful shutdown sequence...")

        # 1. Cease Pooling Execution Updates
        if self.dispatcher:
            logger.info("Halting long-polling execution frames...")
            await self.dispatcher.stop_polling()

        # 2. Terminate Bot Networking Clients
        if self.bot:
            logger.info("Closing active Telegram bot session context windows...")
            await self.bot.session.close()

        # 3. Terminate Cache Infrastructure Sockets
        if self.redis:
            logger.info("Flushing Redis client pools...")
            await self.redis.close()

        # 4. Terminate Database Connection Frameworks
        logger.info("Draining PostgreSQL connection pools...")
        await dispose_engine()

        logger.info("Application context destroyed safely. System termination clean.")

    def register_signal_listeners(self) -> None:
        """Intercepts system termination instructions directly at the event loop tier."""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))


async def main() -> None:
    """Provides application entry parameters to execute safe system run loops."""
    manager = ApplicationLifecycleManager()
    try:
        await manager.initialize()
        manager.register_signal_listeners()
        
        logger.info("Starting polling execution loop parameters. Infrastructure online.")
        # Clear unresolved messages waiting in queue blocks during maintenance/down frames
        await manager.bot.delete_webhook(drop_pending_updates=True)
        await manager.dispatcher.start_polling(manager.bot)
        
    except Exception as critical_fault:
        logger.critical(f"Fatal platform setup failure inside main execution stack: {critical_fault}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Process execution context terminated programmatically.")
        
