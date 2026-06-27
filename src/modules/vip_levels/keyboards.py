"""Production-grade VIP Level Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the VIP tier management subsystem. Implements 
modular builders for tier dashboard navigation, upgrade workflows, and 
benefit comparison views.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class VIPLevelKeyboards:
    """Factory for generating highly responsive VIP tier navigation keyboards."""

    @staticmethod
    def get_vip_menu_keyboard(can_upgrade: bool) -> InlineKeyboardMarkup:
        """Generates the main navigation hub for VIP management."""
        builder = InlineKeyboardBuilder()
        
        if can_upgrade:
            builder.button(text="🚀 Upgrade VIP Level", callback_data="action_upgrade_vip")
        
        builder.button(text="💎 Benefits Comparison", callback_data="vip_benefits")
        builder.button(text="📜 Purchase History", callback_data="vip_history")
        builder.button(text="⬅️ Back to Dashboard", callback_data="nav_home")
        
        builder.adjust(1, 1, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_vip_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the main VIP dashboard."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to VIP", callback_data="nav_vip_dashboard")
        return builder.as_markup()

    @staticmethod
    def get_upgrade_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Generates the final interaction path for VIP upgrades."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Confirm Upgrade", callback_data="action_confirm_upgrade")
        builder.button(text="❌ Cancel", callback_data="nav_vip_dashboard")
        builder.adjust(2)
        return builder.as_markup()
