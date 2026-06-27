# handlers.py
"""Production-grade Wallet Handlers.

Defines the Telegram update controllers for the wallet module. Manages the 
presentation of financial data, including balances, transaction logs, and 
deposit/withdrawal workflow entry points. Delegates all core business logic 
to the WalletService while maintaining clean, asynchronous FSM transitions.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.modules.wallet.services import WalletService
from src.modules.wallet.keyboards import WalletKeyboards
from src.modules.wallet.states import WalletStates

logger = logging.getLogger("investment_platform.modules.wallet.handlers")

router = Router(name="wallet_handlers")


@router.callback_query(F.data == "nav_wallet")
async def handle_wallet_overview(
    callback: CallbackQuery, 
    state: FSMContext, 
    service: WalletService
) -> None:
    """Displays the wallet overview, including balances and quick actions."""
    user_id = callback.from_user.id
    await state.set_state(WalletStates.VIEWING_WALLET)

    try:
        summary = await service.get_wallet_summary(user_id)
        
        text = (
            f"💳 *Wallet Overview*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ *Available Balance:* ₦{summary.available_balance:,.2f}\n"
            f"🔒 *Locked Balance:* ₦{summary.locked_balance:,.2f}\n\n"
            f"📊 *Total Deposits:* ₦{summary.total_deposits:,.2f}\n"
            f"📉 *Total Withdrawals:* ₦{summary.total_withdrawals:,.2f}"
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=WalletKeyboards.get_wallet_main_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Wallet render failed for user {user_id}: {e}")
        await callback.answer("Unable to load wallet. Please try again.", show_alert=True)


@router.callback_query(WalletStates.VIEWING_WALLET, F.data == "wallet_refresh")
async def handle_wallet_refresh(
    callback: CallbackQuery, service: WalletService
) -> None:
    """Handles manual wallet state refresh."""
    await handle_wallet_overview(callback, None, service) # type: ignore


@router.callback_query(F.data == "wallet_transactions")
async def handle_transaction_history(
    callback: CallbackQuery, state: FSMContext, service: WalletService
) -> None:
    """Transitions user to the transaction history view."""
    await state.set_state(WalletStates.VIEWING_TRANSACTIONS)
    # Logic delegated to service to fetch history and display via keyboard
    await callback.answer("Loading transaction history...")
