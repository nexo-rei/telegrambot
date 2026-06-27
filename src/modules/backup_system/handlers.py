"""Production-grade Backup System Handlers.

Defines the Telegram update controllers for the platform's disaster recovery 
and data persistence subsystem. Orchestrates administrative workflows for 
initiating database snapshots, managing retention policies, and executing 
secure restoration procedures. Delegates all operational logic and persistence 
state management to the BackupService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.backup_system.services import BackupService

logger = logging.getLogger("investment_platform.modules.backup_system.handlers")

router = Router(name="backup_system_handlers")


@router.message(Command("backup"))
async def handle_backup_dashboard(
    message: Message, service: BackupService
) -> None:
    """Entry point for authorized administrators to access the disaster recovery console."""
    try:
        # Note: Authorization check should be enforced via middleware
        status = await service.get_backup_status()
        
        await message.answer(
            f"💾 *Backup & Disaster Recovery*\n\n"
            f"Last Backup: `{status.last_backup_time}`\n"
            f"Storage Usage: {status.storage_usage_gb} GB\n"
            f"Retention Policy: {status.retention_days} days\n\n"
            f"Select a recovery operation:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error accessing backup console for {message.from_user.id}: {e}")
        await message.answer("Unable to retrieve backup system status.")


@router.callback_query(F.data == "backup_create_now")
async def handle_create_backup(
    callback: CallbackQuery, service: BackupService
) -> None:
    """Triggers an immediate snapshot of platform data."""
    try:
        await callback.answer("Initiating backup...")
        success = await service.trigger_manual_backup()
        
        if success:
            await callback.message.edit_text("✅ Backup completed successfully.")
        else:
            await callback.message.edit_text("❌ Backup process failed.")
            
    except Exception as e:
        logger.error(f"Manual backup trigger error: {e}")
        await callback.answer("An internal error occurred during snapshot.")
