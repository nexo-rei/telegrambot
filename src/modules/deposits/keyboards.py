# keyboards.py
"""Production-grade Deposit Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the deposit subsystem. Implements modular, reusable 
builders for amount selection, payment gateway routing, and transaction 
status monitoring.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DepositKeyboards:
    """Factory for generating highly responsive deposit navigation keyboards."""

    @staticmethod
    def get_cancel_keyboard() -> InlineKeyboardMarkup:
        """Generates a standard cancellation hub."""
        builder = InlineKeyboardBuilder()
        builder.button(text="❌ Cancel", callback_data="nav_wallet")
        return builder.as_markup()

    @staticmethod
    def get_payment_method_keyboard() -> InlineKeyboardMarkup:
        """Generates selection options for supported payment gateways."""
        builder = InlineKeyboardBuilder()
        builder.button(text="💳 Paystack (Card/Transfer)", callback_data="dep_paystack")
        builder.button(text="⬅️ Back", callback_data="wallet_deposit")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_payment_link_keyboard(url: str) -> InlineKeyboardMarkup:
        """Generates a direct payment link and verification trigger."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔗 Proceed to Payment", url=url))
        builder.button(text="🔄 Verify Payment", callback_data="dep_verify")
        builder.button(text="⬅️ Cancel", callback_data="nav_wallet")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_deposit_status_keyboard(reference: str) -> InlineKeyboardMarkup:
        """Generates status refresh and retry options for existing deposits."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Refresh Status", callback_data=f"dep_refresh_{reference}")
        builder.button(text="⬅️ Back to Wallet", callback_data="nav_wallet")
        builder.adjust(1)
        return builder.as_markup()
