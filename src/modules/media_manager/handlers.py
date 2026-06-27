"""Production-grade Media Manager Handlers.

Defines the Telegram update controllers for the platform's multimedia processing 
subsystem. Orchestrates the ingestion, optimization, and transcoding of media 
assets, including images, video, and audio. Delegates all processing, format 
conversion, and storage logic to the MediaManagerService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.media_manager.services import MediaManagerService

logger = logging.getLogger("investment_platform.modules.media_manager.handlers")

router = Router(name="media_manager_handlers")


@router.message(Command("media"))
async def handle_media_dashboard(
    message: Message, service: MediaManagerService
) -> None:
    """Entry point for managing media assets, thumbnails, and transcoding."""
    try:
        stats = await service.get_media_statistics()
        
        await message.answer(
            f"🖼️ *Media Manager Dashboard*\n\n"
            f"Managed Assets: {stats.total_assets}\n"
            f"Processing Queue: {stats.queue_size}\n\n"
            f"Submit media to optimize, generate thumbnails, or transcode.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading media dashboard: {e}")
        await message.answer("Unable to access the media management suite.")


@router.message(F.video | F.photo | F.audio)
async def handle_media_upload(
    message: Message, service: MediaManagerService
) -> None:
    """Routes incoming media types for professional-grade processing."""
    try:
        # Determine media context from incoming message
        media_type = "video" if message.video else "image" if message.photo else "audio"
        file_id = (message.video.file_id if message.video else 
                   message.photo[-1].file_id if message.photo else message.audio.file_id)
        
        await message.answer(f"⏳ Processing {media_type} for optimization...")
        
        metadata = await service.process_media(
            file_id=file_id,
            media_type=media_type,
            user_id=message.from_user.id
        )
        
        await message.answer(
            f"✅ *Media Processed*\n\n"
            f"Format: `{metadata.codec_info}`\n"
            f"Size: `{metadata.file_size_kb} KB`\n"
            f"Status: Ready",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Media processing failure: {e}")
        await message.answer("Failed to optimize media content.")
