"""Production-grade Audit Log Handlers.

Defines the Telegram update controllers for the platform's immutable compliance 
and security auditing subsystem. Orchestrates the secure retrieval and 
visualization of high-privilege administrative actions and sensitive financial 
transactions. Delegates all business logic and query processing to the 
AuditLogService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.audit_logs.services import AuditLogService

logger = logging.getLogger("investment_platform.modules.audit_logs.handlers")

router = Router(name="audit_log_handlers")


@router.message(Command("audit"))
async def handle_audit_dashboard(
    message: Message, service: AuditLogService
) -> None:
    """Entry point for authorized administrators to access the secure audit trail."""
    try:
        # Note: Authorization check enforced via middleware
        stats = await service.get_audit_statistics()
        
        await message.answer(
            f"🔍 *System Audit Trail*\n\n"
            f"Total Audited Events: {stats.total_events}\n"
            f"Financial Audit Entries: {stats.financial_events}\n"
            f"Security Audit Entries: {stats.security_events}\n\n"
            f"Select a category to view the audit timeline:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading audit dashboard for {message.from_user.id}: {e}")
        await message.answer("Unable to access the secure audit facility.")


@router.callback_query(F.data == "audit_view_financial")
async def handle_view_financial_audit(
    callback: CallbackQuery, service: AuditLogService
) -> None:
    """Displays immutable records of financial transactions."""
    try:
        logs = await service.get_audit_entries(category="financial", limit=15)
        
        if not logs:
            await callback.message.edit_text("✅ No financial audit records found.")
            return

        text = "💰 *Financial Audit Trail*\n\n"
        for log in logs:
            text += f"`[{log.timestamp.strftime('%H:%M:%S')}]` Admin `{log.actor_id}`: {log.action}\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error fetching financial audit logs: {e}")
        await callback.answer("Failed to retrieve financial audit records.")
