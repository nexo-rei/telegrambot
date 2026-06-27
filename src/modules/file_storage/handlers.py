"""Production-grade File Storage Handlers.

Defines the Telegram update controllers for the platform's distributed object 
storage subsystem. Manages the ingestion, retrieval, and administrative 
lifecycle of media assets and documents. Delegates all processing, validation, 
and persistence logic to the FileStorageService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, Document, PhotoSize
from aiogram.filters import Command

from src.modules.file_storage.services import FileStorageService

logger = logging.getLogger("investment_platform.modules.file_storage.handlers")

router = Router(name="file_storage_handlers")


@router.message(Command("storage"))
async def handle_storage_dashboard(
    message: Message, service: FileStorageService
) -> None:
    """Entry point for administrators to manage system storage assets."""
    try:
        stats = await service.get_storage_statistics()
        
        await message.answer(
            f"📂 *Object Storage Dashboard*\n\n"
            f"Usage: `{stats.used_space_gb} GB` / `{stats.total_capacity_gb} GB`\n"
            f"Active Files: {stats.file_count}\n\n"
            f"Upload documents or images to manage assets.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading storage dashboard: {e}")
        await message.answer("Unable to retrieve storage status.")


@router.message(F.document | F.photo)
async def handle_file_upload(
    message: Message, service: FileStorageService
) -> None:
    """Handles incoming file attachments for persistent storage."""
    try:
        # Resolve file ID from different message media types
        file_id = message.document.file_id if message.document else message.photo[-1].file_id
        file_name = message.document.file_name if message.document else "image.jpg"
        
        await message.answer("Uploading file...")
        
        result = await service.store_file(
            file_id=file_id,
            name=file_name,
            owner_id=message.from_user.id
        )
        
        await message.answer(f"✅ File stored successfully: `{result.file_path}`")
        
    except Exception as e:
        logger.error(f"Storage upload failure: {e}")
        await message.answer("Failed to persist file in storage.")
