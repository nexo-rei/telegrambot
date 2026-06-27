# handlers.py
"""Production-grade Withdrawal Handlers.

Defines the Telegram update controllers for the withdrawals module. Manages 
user interaction flows for balance extraction, bank account selection, and 
withdrawal confirmation. Delegates all core financial processing to the 
WithdrawalService while maintaining a clean, asynchronous FSM-based 
navigation controller.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.modules.withdrawals.services import WithdrawalService
from src.modules.withdrawals.keyboards import WithdrawalKeyboards
from src.modules.withdrawals.states import WithdrawalStates
from src.modules.withdrawals.dtos import WithdrawalRequestDTO

logger = logging.getLogger("investment_platform.modules.withdrawals.handlers")

router = Router(name="withdrawal_handlers")


@router.callback_query(F.data == "wallet_withdraw")
async def handle_initiate_withdrawal(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Initiates the withdrawal flow by requesting an amount."""
    await state.set_state(WithdrawalStates.WAITING_FOR_WITHDRAWAL_AMOUNT)
    await callback.message.edit_text(
        "➖ *Withdraw Funds*\n\n"
        "Enter the amount you wish to withdraw (NGN):",
        reply_markup=WithdrawalKeyboards.get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(WithdrawalStates.WAITING_FOR_WITHDRAWAL_AMOUNT, F.text.regexp(r"^\d+$"))
async def handle_withdrawal_amount_entry(
    message: Message, state: FSMContext
) -> None:
    """Validates amount and proceeds to account selection."""
    amount = int(message.text)
    await state.update_data(withdrawal_amount=amount)
    
    await state.set_state(WithdrawalStates.WAITING_FOR_BANK_SELECTION)
    await message.answer(
        f"✅ Amount: ₦{amount:,.2f}\n"
        "Select your payout bank account:",
        reply_markup=WithdrawalKeyboards.get_bank_selection_keyboard()
    )


@router.callback_query(WithdrawalStates.WAITING_FOR_BANK_SELECTION, F.data.startswith("bank_"))
async def handle_withdrawal_confirmation(
    callback: CallbackQuery, state: FSMContext, service: WithdrawalService
) -> None:
    """Requests final confirmation before submitting the withdrawal request."""
    user_data = await state.get_data()
    amount = user_data.get("withdrawal_amount")
    account_id = callback.data.replace("bank_", "")
    
    await state.update_data(selected_account=account_id)
    await state.set_state(WithdrawalStates.WAITING_FOR_CONFIRMATION)
    
    await callback.message.edit_text(
        f"⚠️ *Confirm Withdrawal*\n\n"
        f"Amount: ₦{amount:,.2f}\n"
        f"Account ID: `{account_id}`\n\n"
        "This action is irreversible. Proceed?",
        reply_markup=WithdrawalKeyboards.get_confirmation_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(WithdrawalStates.WAITING_FOR_CONFIRMATION, F.data == "confirm_withdraw")
async def handle_submit_withdrawal(
    callback: CallbackQuery, state: FSMContext, service: WithdrawalService
) -> None:
    """Delegates the final withdrawal request to the service layer."""
    user_data = await state.get_data()
    
    try:
        request = WithdrawalRequestDTO(
            user_id=callback.from_user.id,
            amount=user_data.get("withdrawal_amount"),
            account_id=user_data.get("selected_account")
        )
        
        response = await service.submit_withdrawal(request)
        
        await callback.message.edit_text(
            f"✅ *Withdrawal Request Submitted*\n\n"
            f"Reference: `{response.reference}`\n"
            f"Status: *Processing*",
            parse_mode="Markdown"
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Withdrawal submission failed: {e}")
        await callback.answer("Withdrawal failed. Check balance or contact support.", show_alert=True)
