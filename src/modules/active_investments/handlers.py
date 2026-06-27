# handlers.py
"""Production-grade Active Investment Handlers.

Defines the Telegram update controllers for the active portfolio management 
subsystem. Responsible for rendering real-time investment progress, yield 
tracking, and maturity status to the user. Delegates all financial calculations 
and state retrieval logic to the ActiveInvestmentService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.active_investments.services import ActiveInvestmentService

logger = logging.getLogger("investment_platform.modules.active_investments.handlers")

router = Router(name="active_investment_handlers")


@router.callback_query(F.data == "nav_active_investments")
async def handle_list_active_investments(
    callback: CallbackQuery, service: ActiveInvestmentService
) -> None:
    """Displays a list of all current user investments."""
    try:
        investments = await service.get_user_portfolio(callback.from_user.id)
        if not investments:
            await callback.message.edit_text(
                "ℹ️ *No Active Investments*\n\nYou currently have no running investments.",
                reply_markup=None, # Should link to investment_plans navigation
                parse_mode="Markdown"
            )
            return

        await callback.message.edit_text(
            "📈 *Your Active Investments*\n\n"
            f"You have {len(investments)} active positions.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching portfolio for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load your investments.", show_alert=True)


@router.callback_query(F.data.startswith("inv_view_"))
async def handle_view_investment_details(
    callback: CallbackQuery, service: ActiveInvestmentService
) -> None:
    """Displays detailed progress and ROI metrics for a specific investment."""
    investment_id = callback.data.replace("inv_view_", "")
    
    try:
        details = await service.get_investment_details(investment_id)
        await callback.message.edit_text(
            f"💠 *Investment #{investment_id[:8]}*\n\n"
            f"Amount: ₦{details.amount:,.2f}\n"
            f"Status: {details.status.capitalize()}\n"
            f"Progress: {details.progress_percentage}%\n"
            f"Daily Earnings: ₦{details.daily_earnings:,.2f}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching investment {investment_id}: {e}")
        await callback.answer("Could not retrieve investment details.", show_alert=True)
