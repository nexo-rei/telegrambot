# handlers.py
"""Production-grade Gift Code Handlers.

Defines the Telegram update controllers for the promotional gift code redemption 
subsystem. Responsible for facilitating code submission, validating redemption 
eligibility, and displaying promotional outcomes. Delegates all transactional 
business logic to the GiftCodeService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.modules.gift_codes.services import GiftCodeService
from src.modules.gift_codes.keyboards import GiftCodeKeyboards

logger = logging.getLogger("investment_platform.modules.gift_codes.handlers")

router = Router(name="gift_code_handlers")


@router.callback_query(F.data == "nav_gift_codes")
async def handle_gift_codes_home(
    callback: CallbackQuery, service: GiftCodeService
) -> None:
    """Displays the gift code dashboard for code entry and promotion status."""
    await callback.message.edit_text(
        "🎁 *Gift Code Redemption*\n\n"
        "Enter your promotional code to claim your bonus:",
        reply_markup=GiftCodeKeyboards.get_gift_code_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text.startswith("/"))
async def handle_gift_code_input(
    message: Message, service: GiftCodeService, state: FSMContext
) -> None:
    """Processes incoming gift code redemption attempts."""
    code = message.text.strip().upper()
    
    try:
        result = await service.redeem_code(message.from_user.id, code)
        
        if result.success:
            await message.answer(
                f"🎉 *Success!*\n\nRedeemed {code}. ₦{result.amount:,.2f} added to your wallet.",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                f"❌ *Redemption Failed*\n\n{result.message}",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Redemption error for {message.from_user.id}: {e}")
        await message.answer("An internal error occurred. Please try again later.")
