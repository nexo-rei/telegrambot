"""Production-grade Analytics Handlers.

Defines the Telegram update controllers for the platform's business intelligence 
and behavioral analytics subsystem. Processes requests for deep-dive financial 
metrics, user journey tracking, and fraud insight visualization. Delegates all 
data processing and analytical reporting logic to the AnalyticsService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.analytics.services import AnalyticsService

logger = logging.getLogger("investment_platform.modules.analytics.handlers")

router = Router(name="analytics_handlers")


@router.message(Command("analytics"))
async def handle_analytics_dashboard(
    message: Message, service: AnalyticsService
) -> None:
    """Entry point for authorized executives to view business intelligence."""
    # Note: Authorization check should be enforced via middleware or service
    try:
        summary = await service.get_executive_summary()
        
        await message.answer(
            f"📈 *Executive Intelligence Dashboard*\n\n"
            f"Revenue Trend: {summary.revenue_growth}%\n"
            f"Conversion Rate: {summary.conversion_rate}%\n"
            f"Churn Probability: {summary.churn_rate}%\n\n"
            f"Select a data segment for deep-dive analysis.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading executive dashboard for {message.from_user.id}: {e}")
        await message.answer("Unable to retrieve analytical data.")


@router.callback_query(F.data == "analytics_fraud_check")
async def handle_fraud_analytics(
    callback: CallbackQuery, service: AnalyticsService
) -> None:
    """Displays fraud indicator analytics and risk alerts."""
    try:
        alerts = await service.get_fraud_indicators()
        
        text = "🚨 *Fraud Risk Analysis*\n\n"
        if not alerts:
            text += "All systems within normal parameters."
        else:
            text += f"High-risk events detected: {len(alerts)}"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Fraud analytics error: {e}")
        await callback.answer("Error generating fraud insights.")
