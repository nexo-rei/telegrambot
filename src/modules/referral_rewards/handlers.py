# handlers.py
"""Production-grade Referral Reward Handlers.

Defines the Telegram update controllers for the affiliate commission and 
reward distribution subsystem. Manages the user interface for tracking earned 
bonuses, viewing pending commission payouts, and initiating reward claims. 
Delegates all core financial logic to the ReferralRewardService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.referral_rewards.services import ReferralRewardService

logger = logging.getLogger("investment_platform.modules.referral_rewards.handlers")

router = Router(name="referral_reward_handlers")


@router.callback_query(F.data == "nav_rewards")
async def handle_reward_dashboard(
    callback: CallbackQuery, service: ReferralRewardService
) -> None:
    """Displays the reward dashboard including pending and lifetime earnings."""
    try:
        summary = await service.get_reward_summary(callback.from_user.id)
        
        await callback.message.edit_text(
            f"🎁 *Referral Rewards Dashboard*\n\n"
            f"Pending Rewards: ₦{summary.pending_amount:,.2f}\n"
            f"Lifetime Rewards: ₦{summary.lifetime_amount:,.2f}\n\n"
            f"Status: {'✅ Available to Claim' if summary.has_pending else '⏳ No pending rewards'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading rewards for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load reward data.", show_alert=True)


@router.callback_query(F.data == "action_claim_reward")
async def handle_claim_reward(
    callback: CallbackQuery, service: ReferralRewardService
) -> None:
    """Processes the claim request for earned referral commissions."""
    try:
        result = await service.process_reward_claim(callback.from_user.id)
        
        if result.success:
            await callback.answer(f"Claim successful! ₦{result.amount:,.2f} credited.", show_alert=True)
            await handle_reward_dashboard(callback, service)
        else:
            await callback.answer(result.message, show_alert=True)
            
    except Exception as e:
        logger.error(f"Claim processing error for {callback.from_user.id}: {e}")
        await callback.answer("An error occurred during reward claim.", show_alert=True)
