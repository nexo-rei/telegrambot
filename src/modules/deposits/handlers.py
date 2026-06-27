# handlers.py
"""Production-grade Deposit Handlers.

Defines the Telegram update controllers for the deposits module. Handles the 
orchestration of payment initialization, status verification, and UI transitions. 
Delegates all core financial business logic to the DepositService while 
maintaining a stateless controller approach.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.modules.deposits.services import DepositService
from src.modules.deposits.keyboards import DepositKeyboards
from src.modules.deposits.states import DepositStates
from src.modules.deposits.dtos import DepositRequestDTO

logger = logging.getLogger("investment_platform.modules.deposits.handlers")

router = Router(name="deposit_handlers")


@router.callback_query(F.data == "wallet_deposit")
async def handle_initiate_deposit(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Prompts the user to enter a deposit amount."""
    await state.set_state(DepositStates.WAITING_FOR_DEPOSIT_AMOUNT)
    await callback.message.edit_text(
        "💳 *Deposit Funds*\n\n"
        "Please enter the amount you wish to deposit (e.g., 5000):",
        reply_markup=DepositKeyboards.get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(DepositStates.WAITING_FOR_DEPOSIT_AMOUNT, F.text.regexp(r"^\d+$"))
async def handle_deposit_amount_entry(
    message: Message, state: FSMContext, service: DepositService
) -> None:
    """Validates amount and proceeds to payment method selection."""
    amount = int(message.text)
    
    # Store amount in FSM for later use
    await state.update_data(deposit_amount=amount)
    await state.set_state(DepositStates.WAITING_FOR_PAYMENT_METHOD)
    
    await message.answer(
        f"✅ Amount: ₦{amount:,.2f}\n"
        "Please select your preferred payment method:",
        reply_markup=DepositKeyboards.get_payment_method_keyboard()
    )


@router.callback_query(DepositStates.WAITING_FOR_PAYMENT_METHOD, F.data.startswith("dep_"))
async def handle_payment_initialization(
    callback: CallbackQuery, state: FSMContext, service: DepositService
) -> None:
    """Initializes payment session with the chosen gateway."""
    user_data = await state.get_data()
    amount = user_data.get("deposit_amount")
    gateway = callback.data.replace("dep_", "")
    
    try:
        request = DepositRequestDTO(
            user_id=callback.from_user.id,
            amount=amount,
            gateway=gateway
        )
        
        response = await service.initialize_deposit(request)
        
        await callback.message.edit_text(
            f"🚀 *Payment Initialized*\n\n"
            f"Reference: `{response.transaction_reference}`\n"
            f"Please proceed to complete payment:",
            reply_markup=DepositKeyboards.get_payment_link_keyboard(response.checkout_url),
            parse_mode="Markdown"
        )
        await state.set_state(DepositStates.WAITING_FOR_PAYMENT_VERIFICATION)
        
    except Exception as e:
        logger.error(f"Deposit initialization failed: {e}")
        await callback.answer("Payment initialization failed. Please try again.", show_alert=True)
