# handlers.py
"""Production-grade Notification Handlers.

Defines the Telegram update controllers for the multi-channel alert and 
announcement management subsystem. Responsible for facilitating the notification 
center interface, managing read/unread states, and configuring user preferences. 
Delegates all business and state logic to the NotificationService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.notifications.services import NotificationService

logger = logging.getLogger("investment_platform.modules.notifications.handlers")

router = Router(name="notification_handlers")


@router.callback_query(F.data == "nav_notifications")
async def handle_notification_center(
    callback: CallbackQuery, service: NotificationService
) -> None:
    """Displays the user's notification dashboard and unread alerts."""
    try:
        notifications = await service.get_recent_notifications(callback.from_user.id)
        
        if not notifications:
            await callback.message.edit_text(
                "📭 *Notification Center*\n\nNo new notifications.",
                parse_mode="Markdown"
            )
            return

        text = "🔔 *Recent Notifications*\n\n"
        for note in notifications[:5]:
            status = "🔴" if not note.is_read else "⚪"
            text += f"{status} {note.title}\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error loading notifications for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load notifications.", show_alert=True)


@router.callback_query(F.data.startswith("mark_read_"))
async def handle_mark_as_read(
    callback: CallbackQuery, service: NotificationService
) -> None:
    """Processes request to mark a specific notification as read."""
    try:
        notification_id = callback.data.split("_")[-1]
        success = await service.mark_as_read(callback.from_user.id, notification_id)
        
        if success:
            await callback.answer("Marked as read.")
            await handle_notification_center(callback, service)
        else:
            await callback.answer("Failed to update notification status.")
            
    except Exception as e:
        logger.error(f"Update error for {callback.from_user.id}: {e}")
        await callback.answer("An unexpected error occurred.")
