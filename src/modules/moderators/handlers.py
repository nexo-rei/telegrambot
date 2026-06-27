"""Production-grade Moderator Handlers.

Defines the Telegram update controllers for the platform's moderation and 
compliance subsystem. Manages the review of pending financial transactions, 
user behavior enforcement, and ticket escalation queues. Delegates all 
operational business logic and validation to the ModeratorService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.moderators.services import ModeratorService

logger = logging.getLogger("investment_platform.modules.moderators.handlers")

router = Router(name="moderator_handlers")


@router.message(Command("mod"))
async def handle_moderator_dashboard(
    message: Message, service: ModeratorService
) -> None:
    """Entry point for authorized moderators to access the review dashboard."""
    if not await service.is_moderator(message.from_user.id):
        await message.answer("Access denied: Insufficient privileges.")
        return

    try:
        queue_stats = await service.get_review_queue_stats()
        await message.answer(
            f"🛡️ *Moderator Dashboard*\n\n"
            f"Pending Deposits: {queue_stats.pending_deposits}\n"
            f"Pending Withdrawals: {queue_stats.pending_withdrawals}\n"
            f"Assigned Tickets: {queue_stats.assigned_tickets}\n\n"
            f"Select a queue to review:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading moderator dashboard for {message.from_user.id}: {e}")
        await message.answer("An error occurred while loading your queue.")


@router.callback_query(F.data == "mod_review_deposits")
async def handle_review_deposits(
    callback: CallbackQuery, service: ModeratorService
) -> None:
    """Lists pending deposits for moderation review."""
    try:
        deposits = await service.get_pending_deposits()
        
        if not deposits:
            await callback.message.edit_text("✅ No pending deposits to review.")
            return

        text = "📥 *Pending Deposits Review*\n\n"
        for dep in deposits:
            text += f"User: {dep.user_id} | Amount: ₦{dep.amount:,.2f}\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Moderator deposit review error: {e}")
        await callback.answer("Error retrieving deposit queue.")


@router.callback_query(F.data.startswith("mod_suspend_"))
async def handle_suspend_user(
    callback: CallbackQuery, service: ModeratorService
) -> None:
    """Enforces user suspension based on moderation criteria."""
    try:
        user_id = callback.data.split("_")[-1]
        success = await service.suspend_user(int(user_id))
        
        if success:
            await callback.answer(f"User {user_id} suspended.", show_alert=True)
        else:
            await callback.answer("Suspension failed.")
            
    except Exception as e:
        logger.error(f"Suspension action failed: {e}")
        await callback.answer("An error occurred during enforcement.")
