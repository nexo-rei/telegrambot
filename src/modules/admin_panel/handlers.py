# handlers.py
"""Production-grade Admin Panel Handlers.

Defines the Telegram update controllers for the platform's administrative and 
oversight subsystem. Processes privileged commands, manages user records, 
monitors financial flows, and orchestrates system-wide broadcast campaigns. 
Delegates all operational business logic and validation to the AdminPanelService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.admin_panel.services import AdminPanelService
from src.modules.admin_panel.keyboards import AdminPanelKeyboards

logger = logging.getLogger("investment_platform.modules.admin_panel.handlers")

router = Router(name="admin_panel_handlers")


@router.message(Command("admin"))
async def handle_admin_entry(
    message: Message, service: AdminPanelService
) -> None:
    """Entry point for authenticated administrators to the secure control panel."""
    if not await service.is_authorized(message.from_user.id):
        await message.answer("Access denied: Insufficient privileges.")
        return

    try:
        stats = await service.get_dashboard_statistics()
        await message.answer(
            f"🛡️ *Admin Control Panel*\n\n"
            f"Active Users: {stats.user_count}\n"
            f"Pending Deposits: ₦{stats.pending_deposits:,.2f}\n"
            f"Pending Withdrawals: ₦{stats.pending_withdrawals:,.2f}\n\n"
            f"Select an operation to perform:",
            reply_markup=AdminPanelKeyboards.get_admin_dashboard_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard for {message.from_user.id}: {e}")
        await message.answer("Critical error loading administrative data.")


@router.callback_query(F.data == "admin_refresh_stats")
async def handle_refresh_stats(
    callback: CallbackQuery, service: AdminPanelService
) -> None:
    """Refreshes the admin dashboard metrics."""
    try:
        stats = await service.get_dashboard_statistics()
        await callback.message.edit_text(
            f"🛡️ *Admin Control Panel (Refreshed)*\n\n"
            f"Active Users: {stats.user_count}\n"
            f"Pending Deposits: ₦{stats.pending_deposits:,.2f}\n"
            f"Pending Withdrawals: ₦{stats.pending_withdrawals:,.2f}\n\n"
            f"Select an operation to perform:",
            reply_markup=AdminPanelKeyboards.get_admin_dashboard_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer("Dashboard updated.")
    except Exception as e:
        logger.error(f"Admin refresh error: {e}")
        await callback.answer("Refresh failed.")
