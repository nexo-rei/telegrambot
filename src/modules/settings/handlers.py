# handlers.py
"""Production-grade Settings Handlers.

Defines the Telegram update controllers for the platform's user and 
administrative configuration management subsystem. Facilitates the modification 
of preferences regarding notifications, security, privacy, and UI themes. 
Delegates all configuration state persistence and business validation 
logic to the SettingsService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.settings.services import SettingsService

logger = logging.getLogger("investment_platform.modules.settings.handlers")

router = Router(name="settings_handlers")


@router.message(Command("settings"))
async def handle_settings_home(
    message: Message, service: SettingsService
) -> None:
    """Entry point for users to manage their platform preferences and configurations."""
    try:
        user_config = await service.get_user_configuration(message.from_user.id)
        
        await message.answer(
            f"⚙️ *Account Settings*\n\n"
            f"Notifications: `{'Enabled' if user_config.notifications_enabled else 'Disabled'}`\n"
            f"Language: `{user_config.language}`\n"
            f"Theme: `{user_config.theme}`\n\n"
            f"Select a category to modify:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading settings for {message.from_user.id}: {e}")
        await message.answer("Unable to load account configuration.")


@router.callback_query(F.data.startswith("settings_toggle_"))
async def handle_toggle_setting(
    callback: CallbackQuery, service: SettingsService
) -> None:
    """Processes granular toggle operations for user preference flags."""
    try:
        setting_key = callback.data.split("_")[-1]
        new_value = await service.toggle_setting(callback.from_user.id, setting_key)
        
        await callback.answer(f"✅ {setting_key.capitalize()} updated.")
        
        # Trigger UI refresh or state update
        await callback.message.edit_text(
            f"Settings updated: {setting_key} set to {new_value}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Failed to toggle setting {callback.data}: {e}")
        await callback.answer("Error updating configuration.")
