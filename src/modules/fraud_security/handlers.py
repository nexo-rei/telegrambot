"""Production-grade Fraud Security Handlers.

Defines the Telegram update controllers for the platform's fraud detection 
and threat mitigation subsystem. Facilitates administrative oversight of risk 
assessments, suspicious activity monitoring, and AML/KYC review pipelines. 
Delegates all operational security logic to the FraudSecurityService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.modules.fraud_security.services import FraudSecurityService

logger = logging.getLogger("investment_platform.modules.fraud_security.handlers")

router = Router(name="fraud_security_handlers")


@router.message(Command("fraud_monitor"))
async def handle_fraud_dashboard(
    message: Message, service: FraudSecurityService
) -> None:
    """Entry point for administrators to view real-time fraud risk metrics."""
    try:
        # Authorization verification handled by middleware
        metrics = await service.get_fraud_statistics()
        
        await message.answer(
            f"🛡️ *Fraud Security Dashboard*\n\n"
            f"Active Risk Alerts: {metrics.active_alerts}\n"
            f"Accounts Flagged: {metrics.flagged_accounts}\n"
            f"Average System Risk Score: {metrics.avg_risk_score}\n\n"
            f"Use the menu below to navigate investigation tools:",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error loading fraud dashboard for {message.from_user.id}: {e}")
        await message.answer("Unable to access the fraud monitoring interface.")


@router.callback_query(F.data == "fraud_list_suspicious")
async def handle_list_suspicious_activity(
    callback: CallbackQuery, service: FraudSecurityService
) -> None:
    """Displays the queue of accounts flagged for suspicious behavior."""
    try:
        activities = await service.get_suspicious_activities()
        
        if not activities:
            await callback.message.edit_text("✅ No suspicious activity detected.")
            return

        text = "⚠️ *Suspicious Activity Log*\n\n"
        for activity in activities:
            text += f"• Account: `{activity.user_id}` | Risk: {activity.risk_level}\n"
            
        await callback.message.edit_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error retrieving suspicious activity log: {e}")
        await callback.answer("Failed to load activity log.")
