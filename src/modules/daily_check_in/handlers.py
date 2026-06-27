# handlers.py
"""Production-grade Daily Check-In Handlers.

Defines the Telegram update controllers for the daily engagement and loyalty 
reward subsystem. Responsible for managing user check-in flows, displaying 
streak progression, and notifying users of claimed daily bonuses. Delegates 
all business and state validation logic to the DailyCheckInService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.daily_check_in.services import DailyCheckInService
from src.modules.daily_check_in.keyboards import DailyCheckInKeyboards

logger = logging.getLogger("investment_platform.modules.daily_check_in.handlers")

router = Router(name="daily_check_in_handlers")


@router.callback_query(F.data == "nav_daily_checkin")
async def handle_checkin_dashboard(
    callback: CallbackQuery, service: DailyCheckInService
) -> None:
    """Displays the daily check-in dashboard with current streak and reward status."""
    try:
        status = await service.get_user_status(callback.from_user.id)
        
        await callback.message.edit_text(
            f"📅 *Daily Check-In*\n\n"
            f"Current Streak: {status.current_streak} days\n"
            f"Today's Reward: ₦{status.today_reward:,.2f}\n\n"
            f"Status: {'✅ Checked In' if status.is_checked_in else '⏳ Ready to Claim'}",
            reply_markup=DailyCheckInKeyboards.get_checkin_menu_keyboard(status.is_checked_in),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading check-in dashboard for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load check-in status.", show_alert=True)


@router.callback_query(F.data == "action_perform_checkin")
async def handle_perform_checkin(
    callback: CallbackQuery, service: DailyCheckInService
) -> None:
    """Processes the daily check-in and credits the loyalty bonus."""
    try:
        result = await service.process_checkin(callback.from_user.id)
        
        if result.success:
            await callback.answer(f"Checked in! Received ₦{result.amount:,.2f}.", show_alert=True)
            await handle_checkin_dashboard(callback, service)
        else:
            await callback.answer(result.message, show_alert=True)
            
    except Exception as e:
        logger.error(f"Check-in failure for {callback.from_user.id}: {e}")
        await callback.answer("An error occurred during check-in.", show_alert=True)
