"""Production-grade Log Handlers.

Defines the Telegram update controllers for the platform's diagnostic and 
audit logging subsystem. Facilitates the secure exploration of application 
telemetry, security alerts, and system-wide operational events. Delegates all 
data retrieval and filtering logic to the LogService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.logs.services import LogService

logger = logging.getLogger("investment_platform.modules.logs.handlers")

router = Router(name="log_handlers")


@router.message(Command("logs"))
async def handle_logs_dashboard(
    message: Message, service: LogService
) -> None:
    """Entry point for authorized administrators to access the centralized log explorer."""
    try:
        # Note: Authorization check should be enforced via middleware
        await message.answer(
            "📜 *Log Management Console*\n\n"
            "Select a category to inspect system events:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error accessing log console for {message.from_user.id}: {e}")
        await message.answer("Unable to access the log management system.")


@router.callback_query(F.data == "logs_view_security")
async def handle_view_security_logs(
    callback: CallbackQuery, service: LogService
) -> None:
    """Displays recent security and authentication event logs."""
    try:
        logs = await service.get_recent_logs(category="security", limit=10)
        
        if not logs:
            await callback.message.edit_text("✅ No security logs found.")
            return

        text = "🛡️ *Recent Security Events*\n\n"
        for log in logs:
            text += f"`[{log.timestamp}]` {log.level}: {log.message}\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error fetching security logs: {e}")
        await callback.answer("Failed to retrieve security logs.")
