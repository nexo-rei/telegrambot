# handlers.py
"""Production-grade Transaction Handlers.

Defines the Telegram update controllers for the transaction history and auditing 
subsystem. Responsible for retrieving, filtering, and rendering financial 
records to the user interface. Delegates all data aggregation and formatting 
logic to the TransactionService to maintain controller thinness.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.modules.transactions.services import TransactionService
from src.modules.transactions.keyboards import TransactionKeyboards

logger = logging.getLogger("investment_platform.modules.transactions.handlers")

router = Router(name="transaction_handlers")


@router.callback_query(F.data == "nav_transactions")
async def handle_transaction_home(
    callback: CallbackQuery, service: TransactionService
) -> None:
    """Displays the main transaction history dashboard."""
    try:
        summary = await service.get_recent_summary(callback.from_user.id)
        await callback.message.edit_text(
            "📜 *Transaction History*\n\n"
            f"Recent activity for your account:\n\n"
            f"{summary}",
            reply_markup=TransactionKeyboards.get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading transactions: {e}")
        await callback.answer("Unable to load transactions.", show_alert=True)


@router.callback_query(F.data.startswith("tx_view_"))
async def handle_transaction_details(
    callback: CallbackQuery, service: TransactionService
) -> None:
    """Displays detailed information for a specific transaction."""
    tx_id = callback.data.replace("tx_view_", "")
    
    try:
        details = await service.get_transaction_details(tx_id)
        await callback.message.edit_text(
            f"ℹ️ *Transaction Details*\n\n{details}",
            reply_markup=TransactionKeyboards.get_back_to_history_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching details for {tx_id}: {e}")
        await callback.answer("Could not retrieve transaction details.", show_alert=True)
