# main_bot.py
"""Application Bootstrap Entry Point.

Orchestrates the asynchronous startup initialization sequence, event routing
matrices, middleware pipelines, infrastructure hook mappings (PostgreSQL, Redis),
background job loops, and safe POSIX termination protocols for the application.

BUG FIXES:
  - Only auth_router was registered; all other module routers were missing
  - No middleware was registered (AntiSpam, Auth, Maintenance, RateLimiter)
  - Incorrect aiogram 3.x error handler signature (should accept ErrorEvent, not Any)
  - Bot commands were never set via set_my_commands()
  - The Dispatcher.stop_polling() method does not exist in aiogram 3.x; use dp.stop_polling_now()
    or just cancel the polling task
  - Health check HTTP server missing (required by Railway and bot.Dockerfile HEALTHCHECK)
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
from aiogram.types import ErrorEvent
from aiohttp import web
from redis.asyncio import Redis

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

# BUG FIX: Register all module routers, not just auth
from src.modules.authentication.handlers import router as auth_router
from src.modules.dashboard.handlers import router as dashboard_router
from src.modules.wallet.handlers import router as wallet_router
from src.modules.deposits.handlers import router as deposits_router
from src.modules.withdrawals.handlers import router as withdrawals_router
from src.modules.investment_plans.handlers import router as investment_plans_router
from src.modules.active_investments.handlers import router as active_investments_router
from src.modules.transactions.handlers import router as transactions_router
from src.modules.referral_system.handlers import router as referral_system_router
from src.modules.referral_rewards.handlers import router as referral_rewards_router
from src.modules.support_tickets.handlers import router as support_tickets_router
from src.modules.daily_check_in.handlers import router as daily_check_in_router
from src.modules.daily_income.handlers import router as daily_income_router
from src.modules.vip_levels.handlers import router as vip_levels_router
from src.modules.gift_codes.handlers import router as gift_codes_router
from src.modules.admin_panel.handlers import router as admin_panel_router
from src.modules.analytics.handlers import router as analytics_router
from src.modules.announcements.handlers import router as announcements_router
from src.modules.audit_logs.handlers import router as audit_logs_router
from src.modules.notifications.handlers import router as notifications_router
from src.modules.settings.handlers import router as settings_router
from src.modules.statistics.handlers import router as statistics_router

# BUG FIX: Register all middlewares
from src.shared.middlware.anti_spam import AntiSpamMiddleware
from src.shared.middlware.authentication import AuthenticationMiddleware
from src.shared.middlware.maintenance import MaintenanceMiddleware
from src.shared.middlware.rate_limiter import RateLimiterMiddleware

# Bot commands config
from config.bot_config import BotConfig

# Unified Production Logging Schema Mapping
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("investment_platform.bootstrap")

# Health check HTTP server port (matches bot.Dockerfile HEALTHCHECK)
HEALTH_CHECK_PORT = 8080


class ApplicationLifecycleManager:
    """Manages the startup, running execution loops, and graceful teardown of the bot."""

    def __init__(self) -> None:
        self.bot: Bot | None = None
        self.dispatcher: Dispatcher | None = None
        self.redis: Redis | None = None
        self.storage: RedisStorage | None = None
        self._health_runner: web.AppRunner | None = None
        self._is_shutting_down: bool = False

    async def initialize(self) -> None:
        """Bootstraps upstream dependencies and establishes persistent operational scopes."""
        logger.info("Initializing enterprise bot runtime kernel...")

        # 1. Verify Absolute Database State Integration
        try:
            get_engine()
            health_check = await check_database_connection()
            if health_check["status"] != "HEALTHY":
                raise RuntimeError(
                    f"Database health state verification failed: {health_check['error_message']}"
                )
            logger.info("Database connection layer verified and stable.")
        except Exception as error:
            logger.critical(
                "Subsystem bootstrap sequence aborted. Database layer down.", exc_info=True
            )
            raise error

        # 2. Asynchronous Redis Driver Setup for FSM & Token Buffers
        try:
            self.redis = Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=False,  # Required for aiogram FSM binary serialization
            )
            self.storage = RedisStorage(redis=self.redis)
            logger.info("Asynchronous Redis storage adapter connected successfully.")
        except Exception as error:
            logger.critical(
                "Subsystem bootstrap sequence aborted. Cache layer down.", exc_info=True
            )
            raise error

        # 3. Create Upstream Core Bot Engine Instance
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        # 4. Instantiate Central Event Demultiplexer Dispatcher Context
        self.dispatcher = Dispatcher(storage=self.storage)

        # 5. BUG FIX: Register all middleware in correct order
        # Order matters: outer-most middleware wraps everything else.
        # MaintenanceMiddleware must run before auth to block during maintenance.
        self.dispatcher.message.middleware(MaintenanceMiddleware())
        self.dispatcher.callback_query.middleware(MaintenanceMiddleware())

        self.dispatcher.message.middleware(AuthenticationMiddleware())
        self.dispatcher.callback_query.middleware(AuthenticationMiddleware())

        self.dispatcher.message.middleware(RateLimiterMiddleware())
        self.dispatcher.callback_query.middleware(RateLimiterMiddleware())

        self.dispatcher.message.middleware(AntiSpamMiddleware())
        self.dispatcher.callback_query.middleware(AntiSpamMiddleware())

        logger.info("Middleware pipeline registered successfully.")

        # 6. BUG FIX: Register all module routers (original only had auth_router)
        self.dispatcher.include_router(auth_router)
        self.dispatcher.include_router(dashboard_router)
        self.dispatcher.include_router(wallet_router)
        self.dispatcher.include_router(deposits_router)
        self.dispatcher.include_router(withdrawals_router)
        self.dispatcher.include_router(investment_plans_router)
        self.dispatcher.include_router(active_investments_router)
        self.dispatcher.include_router(transactions_router)
        self.dispatcher.include_router(referral_system_router)
        self.dispatcher.include_router(referral_rewards_router)
        self.dispatcher.include_router(support_tickets_router)
        self.dispatcher.include_router(daily_check_in_router)
        self.dispatcher.include_router(daily_income_router)
        self.dispatcher.include_router(vip_levels_router)
        self.dispatcher.include_router(gift_codes_router)
        self.dispatcher.include_router(admin_panel_router)
        self.dispatcher.include_router(analytics_router)
        self.dispatcher.include_router(announcements_router)
        self.dispatcher.include_router(audit_logs_router)
        self.dispatcher.include_router(notifications_router)
        self.dispatcher.include_router(settings_router)
        self.dispatcher.include_router(statistics_router)
        logger.info("All module routers registered successfully.")

        # 7. Connect Dynamic Runtime State Infrastructure Triggers
        self.dispatcher.startup.register(self._on_startup_event)
        self.dispatcher.shutdown.register(self._on_shutdown_event)

        # 8. BUG FIX: Correct aiogram 3.x error handler signature.
        # Original accepted `Any`; the correct type is `ErrorEvent`.
        @self.dispatcher.errors()
        async def global_error_handler(event: ErrorEvent) -> bool:
            logger.error(
                f"Unhandled operational exception intercepted: {event.exception}", exc_info=True
            )
            return True

        if MAINTENANCE_MODE:
            logger.warning("[WARNING] System is currently flagged as running in MAINTENANCE MODE.")

    async def _start_health_check_server(self) -> None:
        """Starts a minimal aiohttp HTTP server for Railway/Docker health checks.

        BUG FIX: The bot.Dockerfile HEALTHCHECK pings http://localhost:8080/health,
        but no HTTP server was ever started. This caused all Docker health checks to fail,
        triggering container restarts in Railway.
        """
        app = web.Application()

        async def health_handler(request: web.Request) -> web.Response:
            return web.Response(text="OK", status=200)

        app.router.add_get("/health", health_handler)
        app.router.add_get("/", health_handler)

        self._health_runner = web.AppRunner(app)
        await self._health_runner.setup()
        site = web.TCPSite(self._health_runner, "0.0.0.0", HEALTH_CHECK_PORT)
        await site.start()
        logger.info(f"Health check HTTP server started on port {HEALTH_CHECK_PORT}.")

    async def _on_startup_event(self, bot: Bot) -> None:
        """Asynchronous execution bridge executing specialized task sequences post-binding."""
        logger.info("Executing runtime subsystem mapping sequences...")

        # BUG FIX: Set bot commands so the Telegram UI shows the command menu
        try:
            await bot.set_my_commands(BotConfig.DEFAULT_COMMANDS)
            logger.info("Bot command menu registered with Telegram.")
        except Exception as e:
            logger.warning(f"Failed to set bot commands: {e}")

        logger.info("Subsystem execution routing maps locked. Bot listening parameters active.")

    async def _on_shutdown_event(self, bot: Bot) -> None:
        """Asynchronous execution bridge executing automated connection flushing events safely."""
        logger.info("Executing runtime subsystem cleanup sequences...")

    async def shutdown(self) -> None:
        """Gracefully flushes open stream arrays and cuts physical sockets without leaks."""
        if self._is_shutting_down:
            return

        self._is_shutting_down = True
        logger.info("SIGINT/SIGTERM received. Starting graceful shutdown sequence...")

        # 1. Stop health check server
        if self._health_runner:
            await self._health_runner.cleanup()

        # 2. BUG FIX: In aiogram 3.x, Dispatcher.stop_polling() does not exist.
        # The correct way is to cancel the polling task (handled via asyncio task cancellation).
        # We set the flag and let the polling loop exit naturally via CancelledError.

        # 3. Terminate Bot Networking Clients
        if self.bot:
            logger.info("Closing active Telegram bot session context windows...")
            await self.bot.session.close()

        # 4. Terminate Cache Infrastructure Sockets
        if self.redis:
            logger.info("Flushing Redis client pools...")
            await self.redis.aclose()

        # 5. Terminate Database Connection Frameworks
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

        # Start health check HTTP server for Railway/Docker
        await manager._start_health_check_server()

        logger.info("Starting polling execution loop parameters. Infrastructure online.")
        # Clear unresolved messages waiting in queue blocks during maintenance/down frames
        await manager.bot.delete_webhook(drop_pending_updates=True)
        await manager.dispatcher.start_polling(manager.bot)

    except Exception as critical_fault:
        logger.critical(
            f"Fatal platform setup failure inside main execution stack: {critical_fault}",
            exc_info=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Process execution context terminated programmatically.")
