# keyboards.py
"""Production-grade Transaction Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the transaction ledger subsystem. Implements modular 
builders for filtering history, statement generation, and transactional 
drill-down navigation.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TransactionKeyboards:
    """Factory for generating highly responsive transaction history and reporting keyboards."""

    @staticmethod
    def get_main_menu_keyboard() -> InlineKeyboardMarkup:
        """Generates the primary navigation hub for transaction management."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⏳ Pending", callback_data="tx_filter_pending")
        builder.button(text="✅ Completed", callback_data="tx_filter_completed")
        builder.button(text="📊 Statement", callback_data="tx_statement")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_back_to_history_keyboard() -> InlineKeyboardMarkup:
        """Generates a return path to the transaction list view."""
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Back to History", callback_data="nav_transactions")
        return builder.as_markup()

    @staticmethod
    def get_filter_keyboard() -> InlineKeyboardMarkup:
        """Generates interactive filters for specific transaction types."""
        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Deposits", callback_data="tx_type_deposit")
        builder.button(text="➖ Withdrawals", callback_data="tx_type_withdrawal")
        builder.button(text="📈 Investments", callback_data="tx_type_investment")
        builder.button(text="⬅️ Cancel", callback_data="nav_transactions")
        builder.adjust(2)
        return builder.as_markup()
