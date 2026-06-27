# keyboards.py
"""Production-grade Daily Check-In Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the daily loyalty and attendance subsystem. 
Implements modular builders for check-in action triggers, streak history, 
and milestone navigation.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DailyCheckInKeyboards:
    """Factory for generating highly responsive daily check-in navigation keyboards."""

    @staticmethod
    def get_checkin_menu_keyboard(is_checked_in: bool) -> InlineKeyboardMarkup:
        """Generates the navigation hub, toggling check-in button based on status."""
        builder = InlineKeyboardBuilder()
        
        if not is_checked_in:
            builder.button(text="✅ Claim Daily Reward", callback_data="action_perform_checkin")
        else:
            builder.button(text="⭐ Checked In Today", callback_data="no_op")
            
        builder.button(text="📜 History", callback_data="checkin_history")
        builder.button(text="🏆 Milestones", callback_data="checkin_milestones")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        
        builder.adjust(1, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_checkin_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the main daily check-in dashboard."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to Check-In", callback_data="nav_daily_checkin")
        return builder.as_markup()
