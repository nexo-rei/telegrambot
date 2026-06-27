# keyboards.py
"""Production-grade Gift Code Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the gift code and promotional subsystem. 
Implements modular builders for redemption workflows, history views, and 
campaign interaction paths.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class GiftCodeKeyboards:
    """Factory for generating highly responsive gift code navigation keyboards."""

    @staticmethod
    def get_gift_code_menu_keyboard() -> InlineKeyboardMarkup:
        """Generates the main navigation hub for promotional redemption."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🎟 Redeem Code", callback_data="action_enter_code")
        builder.button(text="📜 Redemption History", callback_data="gift_history")
        builder.button(text="🎁 Active Promotions", callback_data="gift_promos")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        builder.adjust(1, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_redemption_result_keyboard() -> InlineKeyboardMarkup:
        """Generates navigation for post-redemption flow."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🏠 Back to Home", callback_data="nav_home")
        builder.button(text="💰 Check Balance", callback_data="nav_wallet")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_back_to_gift_menu_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the main gift code dashboard."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to Gift Menu", callback_data="nav_gift_codes")
        return builder.as_markup()
