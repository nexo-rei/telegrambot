# keyboards.py
"""Production-grade Support Ticket Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the customer support and inquiry management subsystem. 
Implements modular builders for ticket creation workflows, conversation 
threading, and status navigation.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SupportTicketKeyboards:
    """Factory for generating highly responsive support ticket navigation keyboards."""

    @staticmethod
    def get_support_home_keyboard() -> InlineKeyboardMarkup:
        """Generates the main navigation hub for the support portal."""
        builder = InlineKeyboardBuilder()
        builder.button(text="📝 Create New Ticket", callback_data="action_create_ticket")
        builder.button(text="📂 My Open Tickets", callback_data="ticket_list_open")
        builder.button(text="📜 Ticket History", callback_data="ticket_list_closed")
        builder.button(text="❓ View FAQ", callback_data="nav_faq")
        builder.button(text="⬅️ Back to Dashboard", callback_data="nav_home")
        builder.adjust(1, 2, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_ticket_detail_keyboard(ticket_id: str, is_closed: bool) -> InlineKeyboardMarkup:
        """Generates interactive buttons for managing a specific ticket thread."""
        builder = InlineKeyboardBuilder()
        if not is_closed:
            builder.button(text="💬 Reply", callback_data=f"ticket_reply_{ticket_id}")
            builder.button(text="✅ Close Ticket", callback_data=f"ticket_close_{ticket_id}")
        else:
            builder.button(text="🔄 Reopen Ticket", callback_data=f"ticket_reopen_{ticket_id}")
        
        builder.button(text="⬅️ Back to Tickets", callback_data="ticket_list_open")
        builder.adjust(1, 1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_support_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the main support dashboard."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to Support Home", callback_data="nav_support_home")
        return builder.as_markup()
