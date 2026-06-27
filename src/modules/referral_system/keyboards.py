# keyboards.py
"""Production-grade Referral System Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the referral and affiliate tracking subsystem. 
Implements modular builders for dashboard navigation, reward history, and 
social sharing interaction paths.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ReferralKeyboards:
    """Factory for generating highly responsive referral program navigation keyboards."""

    @staticmethod
    def get_referral_menu_keyboard() -> InlineKeyboardMarkup:
        """Generates the main navigation hub for referral activities."""
        builder = InlineKeyboardBuilder()
        builder.button(text="📜 History", callback_data="ref_history")
        builder.button(text="📊 Stats", callback_data="ref_stats")
        builder.button(text="👥 Invited Users", callback_data="ref_team")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        builder.adjust(2, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_referrals_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the main referral dashboard."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to Referrals", callback_data="nav_referrals")
        return builder.as_markup()
