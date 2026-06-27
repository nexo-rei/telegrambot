# keyboards.py
"""Production-grade Authentication Keyboard Builder.

Provides a centralized interface for constructing consistent, premium-UI Telegram 
keyboards for the authentication module. Implements factory methods for generating 
inline and reply keyboards used during registration, onboarding, and session 
management flows.
"""

from typing import Final
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class AuthenticationKeyboards:
    """Factory for generating authentication-related Telegram keyboards."""

    @staticmethod
    def get_terms_keyboard() -> InlineKeyboardMarkup:
        """Generates the Terms and Conditions acceptance interface."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Accept Terms", callback_data="accept_terms")
        builder.button(text="📜 Read Policy", callback_data="read_policy")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_contact_request_keyboard() -> ReplyKeyboardMarkup:
        """Generates the contact-sharing reply keyboard for registration."""
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(
                text="📞 Verify My Phone Number", 
                request_contact=True
            )
        )
        return builder.as_markup(
            resize_keyboard=True, 
            one_time_keyboard=True, 
            input_field_placeholder="Press the button to register"
        )

    @staticmethod
    def get_auth_navigation_keyboard() -> InlineKeyboardMarkup:
        """Generates common authentication navigation options."""
        builder = InlineKeyboardBuilder()
        builder.button(text="Login", callback_data="auth_login")
        builder.button(text="Support", callback_data="auth_support")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_retry_keyboard() -> InlineKeyboardMarkup:
        """Generates a keyboard to allow users to retry a failed operation."""
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Retry Operation", callback_data="auth_retry")
        builder.button(text="❌ Cancel", callback_data="auth_cancel")
        builder.adjust(1)
        return builder.as_markup()
