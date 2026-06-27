# handlers.py
"""Production-grade Authentication Handlers.

Defines the Telegram update controllers for the authentication module. 
Handles user onboarding, registration, and session initialization flows by 
delegating business logic to the AuthenticationService and managing state 
transitions via Aiogram's FSM.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.modules.authentication.services import AuthenticationService
from src.modules.authentication.states import AuthenticationStates
from src.modules.authentication.keyboards import AuthenticationKeyboards

logger = logging.getLogger("investment_platform.modules.authentication.handlers")

router = Router(name="authentication_handlers")


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext, service: AuthenticationService) -> None:
    """Handles the entry point for the bot, determining registration status."""
    user_id = message.from_user.id
    
    if await service.is_registered(user_id):
        await message.answer("Welcome back! Use /dashboard to continue.")
        return

    await state.set_state(AuthenticationStates.ACCEPT_TERMS)
    await message.answer(
        "Welcome to Velorix Investment. Please accept our terms to proceed.",
        reply_markup=AuthenticationKeyboards.get_terms_keyboard()
    )


@router.callback_query(AuthenticationStates.ACCEPT_TERMS, F.data == "accept_terms")
async def process_terms_acceptance(
    callback: CallbackQuery, state: FSMContext, service: AuthenticationService
) -> None:
    """Processes user acceptance of platform terms."""
    if not callback.message:
        return

    await state.set_state(AuthenticationStates.REGISTRATION_PENDING)
    await callback.message.edit_text(
        "Terms accepted. Please share your phone number to complete registration.",
        reply_markup=AuthenticationKeyboards.get_contact_request_keyboard()
    )
    await callback.answer()


@router.message(AuthenticationStates.REGISTRATION_PENDING, F.contact)
async def process_registration(
    message: Message, state: FSMContext, service: AuthenticationService
) -> None:
    """Registers a new user and transitions to the authenticated state."""
    if not message.contact:
        return

    try:
        await service.register_user(
            telegram_id=message.from_user.id,
            phone_number=message.contact.phone_number,
            username=message.from_user.username
        )
        await state.clear()
        await message.answer("Registration successful! Welcome to the platform.")
    except Exception as e:
        logger.error(f"Registration failed for {message.from_user.id}: {e}")
        await message.answer("An error occurred during registration. Please try again later.")


@router.message(Command("logout"))
async def handle_logout(message: Message, service: AuthenticationService) -> None:
    """Handles session termination."""
    await service.logout(message.from_user.id)
    await message.answer("You have been logged out securely.")
