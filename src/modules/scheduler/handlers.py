"""Production-grade Scheduler Handlers.

Defines the Telegram update controllers for the platform's background task and 
job orchestration subsystem. Facilitates administrative control over recurring 
tasks, job queues, and worker health monitoring. Delegates all operational 
logic and state transitions to the SchedulerService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.scheduler.services import SchedulerService

logger = logging.getLogger("investment_platform.modules.scheduler.handlers")

router = Router(name="scheduler_handlers")


@router.message(Command("scheduler"))
async def handle_scheduler_dashboard(
    message: Message, service: SchedulerService
) -> None:
    """Entry point for administrators to manage background task execution."""
    try:
        # Note: Authorization check should be enforced via middleware
        health = await service.get_scheduler_health()
        
        await message.answer(
            f"⚙️ *Scheduler Management Dashboard*\n\n"
            f"Status: `{'Online' if health.is_running else 'Offline'}`\n"
            f"Active Jobs: {health.active_job_count}\n"
            f"Failed Tasks: {health.failed_job_count}\n\n"
            f"Select a management action:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading scheduler dashboard for {message.from_user.id}: {e}")
        await message.answer("Unable to access the background job scheduler.")


@router.callback_query(F.data == "scheduler_list_jobs")
async def handle_list_jobs(
    callback: CallbackQuery, service: SchedulerService
) -> None:
    """Displays the registry of currently scheduled background tasks."""
    try:
        jobs = await service.get_scheduled_jobs()
        
        if not jobs:
            await callback.message.edit_text("✅ No scheduled jobs found.")
            return

        text = "📋 *Scheduled Jobs*\n\n"
        for job in jobs:
            text += f"• `{job.name}` (Next: {job.next_run})\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error retrieving job list: {e}")
        await callback.answer("Failed to list scheduled jobs.")
