# keyboards.py
"""Production-grade Wallet Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the wallet subsystem. Implements modular, reusable 
builders for deposit, withdrawal, and transaction management workflows to 
ensure a consistent and professional user experience.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class WalletKeyboards:
    """Factory for generating highly responsive wallet navigation keyboards."""

    @staticmethod
    def get_wallet_main_keyboard() -> InlineKeyboardMarkup:
        """Generates the primary navigation hub for wallet operations."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="➕ Deposit Funds", callback_data="wallet_deposit")
        builder.button(text="➖ Withdraw Funds", callback_data="wallet_withdraw")
        builder.button(text="📜 Transactions", callback_data="wallet_transactions")
        builder.button(text="🔄 Refresh Balance", callback_data="wallet_refresh")
        builder.button(text="⬅️ Back to Dashboard", callback_data="nav_dashboard")
        
        builder.adjust(2, 1, 2)
        return builder.as_markup()

    @staticmethod
    def get_deposit_method_keyboard() -> InlineKeyboardMarkup:
        """Generates selection options for deposit gateways."""
        builder = InlineKeyboardBuilder()
        builder.button(text="Paystack (NGN)", callback_data="dep_paystack")
        builder.button(text="Manual Transfer", callback_data="dep_manual")
        builder.button(text="⬅️ Cancel", callback_data="nav_wallet")
        
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_transaction_history_keyboard() -> InlineKeyboardMarkup:
        """Generates navigation for browsing transaction history."""
        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Previous", callback_data="tx_prev")
        builder.button(text="Next ▶️", callback_data="tx_next")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        
        builder.adjust(2, 1)
        return builder.as_markup()
