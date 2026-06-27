# handlers.py
"""Production-grade Daily Income Handlers.

Defines the Telegram update controllers for the daily earnings distribution 
subsystem. Responsible for rendering income summaries, facilitating 
ROI claims, and displaying performance history to the end user. 
Delegates all operational business logic to the DailyIncomeService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.daily_income.services import DailyIncomeService

logger = logging.getLogger("investment_platform.modules.daily_income.handlers")

router = Router(name="daily_income_handlers")


@router.callback_query(F.data == "nav_daily_income")
async def handle_income_dashboard(
    callback: CallbackQuery, service: DailyIncomeService
) -> None:
    """Displays the daily income dashboard with claimable balance."""
    try:
        earnings = await service.get_user_earnings_summary(callback.from_user.id)
        
        await callback.message.edit_text(
            f"📅 *Daily Income Dashboard*\n\n"
            f"Today's Earnings: ₦{earnings.daily_amount:,.2f}\n"
            f"Total Claimable: ₦{earnings.total_claimable:,.2f}\n"
            f"Lifetime Earnings: ₦{earnings.lifetime_total:,.2f}\n\n"
            f"Status: {'✅ Ready to Claim' if earnings.is_claimable else '⏳ Processing'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading daily income for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load income dashboard.", show_alert=True)


@router.callback_query(F.data == "action_claim_income")
async def handle_claim_income(
    callback: CallbackQuery, service: DailyIncomeService
) -> None:
    """Processes the claim request for accumulated daily ROI."""
    try:
        result = await service.process_daily_claim(callback.from_user.id)
        
        if result.success:
            await callback.answer(f"Success! ₦{result.amount:,.2f} added to wallet.", show_alert=True)
            await handle_income_dashboard(callback, service)
        else:
            await callback.answer(result.message, show_alert=True)
            
    except Exception as e:
        logger.error(f"Claim failure for {callback.from_user.id}: {e}")
        await callback.answer("An internal error occurred during claim.", show_alert=True)
