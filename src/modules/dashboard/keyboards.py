# keyboards.py
"""Production-grade Dashboard Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces. Implements modular, reusable builders for all dashboard 
actions, facilitating consistent UX across the platform's investment 
and account management features.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DashboardKeyboards:
    """Factory for generating highly responsive dashboard navigation keyboards."""

    @staticmethod
    def get_main_menu_keyboard() -> InlineKeyboardMarkup:
        """Generates the primary navigation hub for the dashboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="💰 Wallet", callback_data="nav_wallet")
        builder.button(text="📈 Investments", callback_data="nav_investments")
        builder.button(text="👥 Referral", callback_data="nav_referral")
        builder.button(text="💎 VIP Levels", callback_data="nav_vip")
        builder.button(text="🔄 Refresh", callback_data="dashboard_refresh")
        builder.button(text="⚙️ Settings", callback_data="nav_settings")
        
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_wallet_actions_keyboard() -> InlineKeyboardMarkup:
        """Generates quick-action buttons for financial operations."""
        builder = InlineKeyboardBuilder()
        builder.button(text="➕ Deposit", callback_data="wallet_deposit")
        builder.button(text="➖ Withdraw", callback_data="wallet_withdraw")
        builder.button(text="⬅️ Back", callback_data="nav_dashboard")
        
        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def get_investment_navigation_keyboard() -> InlineKeyboardMarkup:
        """Generates navigation options for investment management."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✨ New Investment", callback_data="inv_plans")
        builder.button(text="📊 My Portfolio", callback_data="inv_active")
        builder.button(text="⬅️ Home", callback_data="nav_dashboard")
        
        builder.adjust(1)
        return builder.as_markup()
