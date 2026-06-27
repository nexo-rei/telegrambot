# bot_config.py
"""Bot Specific Operational Configuration Engine.

Integrates global application structural parameters with specific execution rules
dictated by aiogram framework properties, rate limit configurations, and local
Nigerian investment platform runtime conditions.
"""

from enum import Enum
from typing import Any, Dict, List
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config.base import settings


class Environment(str, Enum):
    """Runtime execution environment definitions."""
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class BotConfig:
    """Production-ready configurations dedicated to the Telegram bot execution layer.

    Binds global state properties with targeted runtime metrics like timeouts,
    rate-limits, and localized text interfaces for the Nigerian target client.
    """

    # Project Metadata
    PROJECT_NAME: str = "investment_platform"
    VERSION: str = "1.0.0"
    
    # Core Identity Configuration
    TOKEN: str = settings.bot.TOKEN
    USERNAME: str = settings.bot.USERNAME
    DEFAULT_PROPERTIES: DefaultBotProperties = DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        protect_content=True
    )

    # Localization Parameters
    DEFAULT_LANGUAGE: str = "en"
    CURRENCY: str = settings.payment.CURRENCY
    CURRENCY_SYMBOL: str = settings.payment.CURRENCY_SYMBOL
    TIMEZONE: str = settings.scheduler.TIMEZONE

    # Media & Network Restrictions
    MAX_UPLOAD_SIZE_BYTES: int = 52_428_800  # 50MB production ceiling limit
    SESSION_TIMEOUT_SECONDS: float = 60.0
    CALLBACK_EXPIRATION_SECONDS: int = 86_400  # 24-hour state frame validity

    # Security Rate Limiting Matrix
    # Dictated as: max_requests / time_window_seconds
    DEFAULT_RATE_LIMITS: Dict[str, Dict[str, Any]] = {
        "private_chat": {"requests": 3, "window": 1.0},
        "callback_query": {"requests": 5, "window": 1.0},
        "financial_action": {"requests": 1, "window": 5.0}
    }

    # Communication Infrastructure Layout Options
    IS_WEBHOOK_ENABLED: bool = settings.flags.ENABLE_WEBHOOK
    WEBHOOK_URL: str | None = settings.bot.WEBHOOK_URL
    
    POLLING_OPTIONS: Dict[str, Any] = {
        "skip_updates": True,
        "timeout": 30,
        "allowed_updates": ["message", "callback_query", "pre_checkout_query", "shipping_query"]
    }

    # Administrative Operational Commands Setup
    DEFAULT_COMMANDS: List[BotCommand] = [
        BotCommand(command="start", description="Initialize platform or refresh main interface"),
        BotCommand(command="dashboard", description="Render personal NGN portfolio metrics"),
        BotCommand(command="wallet", description="Manage capital funding and extraction tracking"),
        BotCommand(command="invest", description="Access active premium asset investment tiers"),
        BotCommand(command="referrals", description="Review structural multi-level affiliate trees"),
        BotCommand(command="support", description="Open a verified internal helpdesk interaction ticket"),
        BotCommand(command="help", description="Review core architectural rules and mechanics overview")
    ]

    # Localization Event Messaging Broadcast Strings
    STARTUP_MESSAGE: str = (
        f"<b>[SYSTEM_INITIALIZATION]</b> 🚀\n"
        f"Platform Name: <code>{PROJECT_NAME}</code> (v{VERSION})\n"
        f"Status: Operational\n"
        f"Base Asset Configuration: {CURRENCY_SYMBOL} ({CURRENCY})\n"
        f"Local Engine Target: <code>{TIMEZONE}</code>\n"
        f"Event Log Trace: Polling loop connection verified successfully."
    )

    SHUTDOWN_MESSAGE: str = (
        f"<b>[SYSTEM_SHUTDOWN]</b> ⚠️\n"
        f"Platform Name: <code>{PROJECT_NAME}</code>\n"
        f"Execution Message: SIGTERM hook intercepted successfully. Halting polling engines..."
    )

    @classmethod
    def get_environment(cls) -> Environment:
        """Derives the current processing runtime contextual execution tier."""
        return Environment.DEVELOPMENT if settings.flags.DEBUG else Environment.PRODUCTION

    @classmethod
    def get_webhook_config(cls) -> Dict[str, Any]:
        """Assembles verified dynamic hook parameter structures.

        Raises:
            ValueError: Critical configuration trace failure when components are missing.
        """
        if cls.IS_WEBHOOK_ENABLED and not cls.WEBHOOK_URL:
            raise ValueError("Runtime error: WEBHOOK_URL must be specified when ENABLE_WEBHOOK is true.")
        
        return {
            "url": cls.WEBHOOK_URL,
            "drop_pending_updates": True,
            "max_connections": 100
        }
        
