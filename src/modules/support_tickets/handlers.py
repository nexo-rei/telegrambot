# handlers.py
"""Production-grade Support Ticket Handlers.

Defines the Telegram update controllers for the customer support and inquiry 
resolution subsystem. Manages the ticket creation lifecycle, interactive 
conversation threads, and status monitoring. Delegates all business and 
state validation logic to the SupportTicketService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from src.modules.support_tickets.services import SupportTicketService
from src.modules.support_tickets.keyboards import SupportTicketKeyboards

logger = logging.getLogger("investment_platform.modules.support_tickets.handlers")

router = Router(name="support_ticket_handlers")


@router.callback_query(F.data == "nav_support_home")
async def handle_support_dashboard(
    callback: CallbackQuery, service: SupportTicketService
) -> None:
    """Displays the main support portal, including open tickets and FAQs."""
    try:
        active_count = await service.get_open_ticket_count(callback.from_user.id)
        
        await callback.message.edit_text(
            f"🎧 *Support Center*\n\n"
            f"You have {active_count} active tickets.\n"
            f"Our team aims to respond within 2 hours.",
            reply_markup=SupportTicketKeyboards.get_support_home_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading support dashboard for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load support portal.", show_alert=True)


@router.callback_query(F.data == "action_create_ticket")
async def handle_create_ticket_flow(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Initiates the ticket creation flow."""
    await state.set_state("waiting_for_subject")
    await callback.message.edit_text(
        "📝 *New Ticket*\n\nPlease enter the subject of your inquiry:",
        reply_markup=SupportTicketKeyboards.get_back_to_support_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.state == "waiting_for_subject")
async def handle_ticket_subject(message: Message, state: FSMContext) -> None:
    """Captures ticket subject and progresses the flow."""
    await state.update_data(subject=message.text)
    await state.set_state("waiting_for_description")
    await message.answer("Great. Now, please describe your issue in detail.")


@router.message(F.state == "waiting_for_description")
async def handle_ticket_submission(
    message: Message, state: FSMContext, service: SupportTicketService
) -> None:
    """Finalizes ticket creation and persists data via the service."""
    data = await state.get_data()
    try:
        ticket = await service.create_ticket(
            user_id=message.from_user.id,
            subject=data["subject"],
            description=message.text
        )
        
        await message.answer(f"✅ Ticket #{ticket.id} created successfully.")
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ticket creation failed for {message.from_user.id}: {e}")
        await message.answer("An error occurred while submitting your ticket.")
        await state.clear()
