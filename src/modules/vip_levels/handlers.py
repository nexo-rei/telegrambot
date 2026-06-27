# handlers.py
"""Production-grade VIP Level Handlers.

Defines the Telegram update controllers for the premium tier and loyalty 
management subsystem. Responsible for rendering the VIP dashboard, comparing 
tier benefits, and initiating upgrade workflows. Delegates all business 
logic, tier validation, and financial calculations to the VIPLevelService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.vip_levels.services import VIPLevelService
from src.modules.vip_levels.keyboards import VIPLevelKeyboards

logger = logging.getLogger("investment_platform.modules.vip_levels.handlers")

router = Router(name="vip_level_handlers")


@router.callback_query(F.data == "nav_vip_dashboard")
async def handle_vip_dashboard(
    callback: CallbackQuery, service: VIPLevelService
) -> None:
    """Displays the user's current VIP tier, status, and upgrade path."""
    try:
        status = await service.get_user_vip_status(callback.from_user.id)
        
        await callback.message.edit_text(
            f"💎 *VIP Level Dashboard*\n\n"
            f"Current Level: {status.level_name}\n"
            f"Cashback Rate: {status.cashback_rate}%\n"
            f"Progress to Next: {status.progress}%\n\n"
            f"Unlock next tier benefits for ₦{status.upgrade_cost:,.2f}",
            reply_markup=VIPLevelKeyboards.get_vip_menu_keyboard(
                can_upgrade=status.can_upgrade
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading VIP dashboard for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load VIP data.", show_alert=True)


@router.callback_query(F.data == "action_upgrade_vip")
async def handle_vip_upgrade(
    callback: CallbackQuery, service: VIPLevelService
) -> None:
    """Processes the request to purchase the next VIP level."""
    try:
        result = await service.process_upgrade(callback.from_user.id)
        
        if result.success:
            await callback.answer(f"Success! You are now {result.new_level}.", show_alert=True)
            await handle_vip_dashboard(callback, service)
        else:
            await callback.answer(result.message, show_alert=True)
            
    except Exception as e:
        logger.error(f"VIP upgrade error for {callback.from_user.id}: {e}")
        await callback.answer("An error occurred during upgrade processing.", show_alert=True)
