# keyboards.py
"""Production-grade Admin Panel Keyboard Builder.

Provides a centralized factory for constructing high-privilege Telegram 
administrative interfaces. Implements modular builders for financial auditing, 
user governance, and system-wide broadcast orchestration, ensuring a secure 
and responsive management experience.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AdminPanelKeyboards:
    """Factory for generating premium administrative control interfaces."""

    @staticmethod
    def get_admin_dashboard_keyboard() -> InlineKeyboardMarkup:
        """Generates the main navigation hub for system administrators."""
        builder = InlineKeyboardBuilder()
        builder.button(text="👥 User Management", callback_data="admin_users")
        builder.button(text="💰 Financial Ops", callback_data="admin_finance")
        builder.button(text="📢 Broadcasts", callback_data="admin_broadcast")
        builder.button(text="🎧 Support Queue", callback_data="admin_support")
        builder.button(text="⚙️ System Health", callback_data="admin_health")
        builder.button(text="🔄 Refresh Dashboard", callback_data="admin_refresh_stats")
        builder.adjust(2, 2, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_financial_management_keyboard() -> InlineKeyboardMarkup:
        """Generates navigation for deposit/withdrawal auditing."""
        builder = InlineKeyboardBuilder()
        builder.button(text="📥 Approve Deposits", callback_data="admin_finance_deposits")
        builder.button(text="📤 Approve Withdrawals", callback_data="admin_finance_withdrawals")
        builder.button(text="⬅️ Back to Dashboard", callback_data="admin_dashboard")
        builder.adjust(1, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_confirmation_keyboard(action_id: str) -> InlineKeyboardMarkup:
        """Generates a secure two-step confirmation dialog for privileged actions."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Confirm", callback_data=f"confirm_{action_id}")
        builder.button(text="❌ Cancel", callback_data="admin_dashboard")
        builder.adjust(2)
        return builder.as_markup()
