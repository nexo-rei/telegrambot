# handlers.py
"""Production-grade Referral System Handlers.

Defines the Telegram update controllers for the referral and affiliate management 
subsystem. Responsible for exposing the user's invite link, tracking referral 
statistics, and rendering reward history. Delegates all business logic and 
data aggregation to the ReferralService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from src.modules.referral_system.services import ReferralService
from src.modules.referral_system.keyboards import ReferralKeyboards

logger = logging.getLogger("investment_platform.modules.referral_system.handlers")

router = Router(name="referral_handlers")


@router.callback_query(F.data == "nav_referrals")
async def handle_referral_dashboard(
    callback: CallbackQuery, service: ReferralService
) -> None:
    """Displays the main referral dashboard, invite links, and reward stats."""
    try:
        stats = await service.get_user_stats(callback.from_user.id)
        invite_link = await create_start_link(callback.bot, f"ref_{callback.from_user.id}")
        
        await callback.message.edit_text(
            f"🔗 *Referral Program*\n\n"
            f"Invite friends and earn commissions!\n\n"
            f"Total Referrals: {stats.total_referrals}\n"
            f"Total Earned: ₦{stats.total_earned:,.2f}\n\n"
            f"Your Invite Link:\n`{invite_link}`",
            reply_markup=ReferralKeyboards.get_referral_menu_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading referral dashboard for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load referral data.", show_alert=True)


@router.callback_query(F.data == "ref_history")
async def handle_referral_history(
    callback: CallbackQuery, service: ReferralService
) -> None:
    """Displays the history of successful referrals and earned commissions."""
    try:
        history = await service.get_referral_history(callback.from_user.id)
        await callback.message.edit_text(
            f"📜 *Referral History*\n\n{history}",
            reply_markup=ReferralKeyboards.get_back_to_referrals_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching referral history for {callback.from_user.id}: {e}")
        await callback.answer("Could not retrieve referral history.", show_alert=True)
