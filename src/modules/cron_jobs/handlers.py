"""Production-grade Cron Job Handlers.

Defines the Telegram update controllers for the platform's time-based task 
management subsystem. Facilitates administrative oversight of scheduled recurring 
operations, cron health, and task execution lifecycle. Delegates all business 
logic and operational state management to the CronJobService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.cron_jobs.services import CronJobService

logger = logging.getLogger("investment_platform.modules.cron_jobs.handlers")

router = Router(name="cron_job_handlers")


@router.message(Command("cron"))
async def handle_cron_dashboard(
    message: Message, service: CronJobService
) -> None:
    """Entry point for administrators to view and manage the cron registry."""
    try:
        # Authorization check via middleware or service
        stats = await service.get_cron_statistics()
        
        await message.answer(
            f"🕒 *Cron Jobs Management*\n\n"
            f"Active Jobs: {stats.active_count}\n"
            f"Disabled Jobs: {stats.disabled_count}\n"
            f"Recent Failures: {stats.failure_count}\n\n"
            f"Select a management category:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading cron dashboard for {message.from_user.id}: {e}")
        await message.answer("Unable to access the cron management system.")


@router.callback_query(F.data == "cron_trigger_manual")
async def handle_trigger_cron(
    callback: CallbackQuery, service: CronJobService
) -> None:
    """Manually triggers the execution of a registered background cron job."""
    try:
        # Note: In production, job_id would be retrieved from callback data
        success = await service.trigger_manual_execution(job_id="daily_payout")
        
        if success:
            await callback.answer("✅ Cron job execution initiated.", show_alert=True)
        else:
            await callback.answer("❌ Failed to initiate job.")
            
    except Exception as e:
        logger.error(f"Manual cron trigger error: {e}")
        await callback.answer("An internal error occurred.")
