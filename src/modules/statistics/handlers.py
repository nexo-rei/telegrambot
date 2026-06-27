"""Production-grade Statistics Handlers.

Defines the Telegram update controllers for the platform's analytical and 
reporting subsystem. Processes requests for platform KPIs, financial growth 
metrics, and investment performance dashboards. Delegates all data aggregation 
and computational logic to the StatisticsService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.modules.statistics.services import StatisticsService

logger = logging.getLogger("investment_platform.modules.statistics.handlers")

router = Router(name="statistics_handlers")


@router.callback_query(F.data == "nav_stats_home")
async def handle_statistics_home(
    callback: CallbackQuery, service: StatisticsService
) -> None:
    """Displays the administrative platform overview dashboard."""
    try:
        # Check authorization via service/auth integration if required
        stats = await service.get_platform_overview()
        
        text = (
            "📊 *Platform Statistics Overview*\n\n"
            f"👥 Total Users: {stats.total_users}\n"
            f"📈 Active Today: {stats.active_users}\n"
            f"💰 Total Revenue: ₦{stats.total_revenue:,.2f}\n"
            f"💎 VIP Users: {stats.vip_count}\n\n"
            "Select a category for detailed insights."
        )
        
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error rendering statistics for {callback.from_user.id}: {e}")
        await callback.answer("Unable to load statistics.", show_alert=True)


@router.callback_query(F.data == "stats_refresh")
async def handle_refresh_statistics(
    callback: CallbackQuery, service: StatisticsService
) -> None:
    """Triggers an update of the statistical cache and re-renders the dashboard."""
    try:
        await service.refresh_cache()
        await handle_statistics_home(callback, service)
        await callback.answer("Statistics cache refreshed.")
        
    except Exception as e:
        logger.error(f"Failed to refresh stats: {e}")
        await callback.answer("Refresh failed.")
