# handlers.py
"""Production-grade Dashboard Handlers.

Defines the Telegram update controllers for the dashboard module. 
Handles the presentation of financial summaries, investment tracking, and 
user profile navigation by delegating business logic to the DashboardService 
and managing UI updates via premium, formatted messages and keyboards.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.modules.dashboard.services import DashboardService
from src.modules.dashboard.keyboards import DashboardKeyboards
from src.modules.dashboard.states import DashboardStates

logger = logging.getLogger("investment_platform.modules.dashboard.handlers")

router = Router(name="dashboard_handlers")


@router.message(Command("dashboard"))
@router.callback_query(F.data == "nav_dashboard")
async def handle_dashboard_view(
    update: Message | CallbackQuery, 
    state: FSMContext, 
    service: DashboardService
) -> None:
    """Displays the premium dashboard overview for the user."""
    user_id = update.from_user.id
    await state.set_state(DashboardStates.MAIN_VIEW)

    try:
        # Fetch consolidated dashboard data from service
        summary = await service.get_user_summary(user_id)
        
        # Determine message target
        msg = update if isinstance(update, Message) else update.message
        
        # Render premium UI
        text = (
            f"👤 *Account Summary*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Wallet:* ₦{summary.balance:,.2f}\n"
            f"📈 *Active Investments:* {summary.active_investments}\n"
            f"💎 *VIP Level:* {summary.vip_level}\n\n"
            f"📊 *Today's Earnings:* ₦{summary.daily_earnings:,.2f}\n"
            f"🌍 *Total Referral Bonus:* ₦{summary.referral_earnings:,.2f}"
        )

        if isinstance(update, CallbackQuery):
            await update.message.edit_text(
                text=text,
                reply_markup=DashboardKeyboards.get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
            await update.answer()
        else:
            await update.answer(
                text=text,
                reply_markup=DashboardKeyboards.get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Dashboard render failed for {user_id}: {e}")
        error_msg = "Unable to load dashboard. Please try again."
        if isinstance(update, CallbackQuery):
            await update.message.answer(error_msg)
        else:
            await update.answer(error_msg)


@router.callback_query(F.data == "dashboard_refresh")
async def handle_dashboard_refresh(
    callback: CallbackQuery, service: DashboardService
) -> None:
    """Handles manual dashboard refresh requests."""
    await handle_dashboard_view(callback, None, service) # type: ignore
