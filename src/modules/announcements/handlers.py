# handlers.py
"""Production-grade Announcement Handlers.

Defines the Telegram update controllers for the system-wide broadcast and 
announcement management subsystem. Responsible for managing the announcement 
feed, rendering detailed notices, and handling user interactions with 
promotional campaigns. Delegates all business and state validation logic 
to the AnnouncementService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.announcements.services import AnnouncementService

logger = logging.getLogger("investment_platform.modules.announcements.handlers")

router = Router(name="announcement_handlers")


@router.callback_query(F.data == "nav_announcements")
async def handle_announcement_feed(
    callback: CallbackQuery, service: AnnouncementService
) -> None:
    """Displays the latest system announcements and pinned notices."""
    try:
        announcements = await service.get_latest_announcements(limit=5)
        
        if not announcements:
            await callback.message.edit_text(
                "📢 *Announcements*\n\nNo new updates at this time.",
                parse_mode="Markdown"
            )
            return

        text = "📢 *Latest Announcements*\n\n"
        for ann in announcements:
            text += f"• *{ann.title}* ({ann.pub_date})\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error loading announcement feed for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load announcements.", show_alert=True)


@router.callback_query(F.data.startswith("announcement_view_"))
async def handle_view_announcement(
    callback: CallbackQuery, service: AnnouncementService
) -> None:
    """Renders the detailed view of a specific announcement."""
    try:
        ann_id = callback.data.split("_")[-1]
        announcement = await service.get_announcement_details(ann_id)
        
        if not announcement:
            await callback.answer("Announcement not found.")
            return

        await callback.message.edit_text(
            f"📢 *{announcement.title}*\n\n{announcement.content}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error viewing announcement {callback.data}: {e}")
        await callback.answer("An error occurred while loading the notice.")
