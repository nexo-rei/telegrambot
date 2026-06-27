# keyboards.py
"""Production-grade Withdrawal Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the withdrawal subsystem. Implements modular, 
reusable builders for bank selection, transaction confirmation, and 
lifecycle status monitoring to ensure a professional user experience.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class WithdrawalKeyboards:
    """Factory for generating highly responsive withdrawal navigation keyboards."""

    @staticmethod
    def get_cancel_keyboard() -> InlineKeyboardMarkup:
        """Generates a standard cancellation hub to return to wallet."""
        builder = InlineKeyboardBuilder()
        builder.button(text="❌ Cancel", callback_data="nav_wallet")
        return builder.as_markup()

    @staticmethod
    def get_bank_selection_keyboard() -> InlineKeyboardMarkup:
        """Generates selectable bank accounts for payout processing."""
        builder = InlineKeyboardBuilder()
        # Mock bank data integration
        builder.button(text="🏦 Zenith Bank - ****1234", callback_data="bank_zenith_1234")
        builder.button(text="➕ Add New Bank Account", callback_data="bank_add_new")
        builder.button(text="⬅️ Back", callback_data="wallet_withdraw")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Generates final withdrawal submission confirmation buttons."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Confirm & Submit", callback_data="confirm_withdraw")
        builder.button(text="❌ Cancel", callback_data="nav_wallet")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_status_keyboard(reference: str) -> InlineKeyboardMarkup:
        """Generates status refresh and history navigation for withdrawals."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Refresh Status", callback_data=f"wdr_refresh_{reference}")
        builder.button(text="📜 Withdrawal History", callback_data="wdr_history")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        builder.adjust(1)
        return builder.as_markup()
