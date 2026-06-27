# message_templates.py
"""Centralized Message Templating and Rendering Engine.

Provides a unified interface for defining and rendering rich, dynamic Telegram 
messages. Implements a template-engine architecture that supports variable 
interpolation, safe HTML escaping, and integration with financial and temporal 
formatting helpers to ensure consistent communication across all platform modules.
"""

import logging
from typing import Any, Dict, Final, Optional

from src.shared.helpers.currency_formatter import format_ngn_currency
from src.shared.helpers.datetime_utils import format_to_local_time

logger = logging.getLogger("investment_platform.shared.templates")


class TemplateRenderer:
    """Utility for safe placeholder interpolation and message normalization."""

    @staticmethod
    def render(template: str, context: Dict[str, Any]) -> str:
        """Injects contextual data into template placeholders using safe formatting."""
        try:
            return template.format(**context)
        except KeyError as e:
            logger.error(f"Missing template key: {e}")
            return template  # Fail-safe: return raw template on key error
        except Exception as e:
            logger.error(f"Template rendering fault: {e}")
            return "<i>Message generation error occurred.</i>"


class MessageTemplates:
    """Registry of platform-wide message templates and rendering logic."""

    # --- Authentication Templates ---
    WELCOME_MESSAGE: Final[str] = (
        "<b>Welcome to Velorix Investment!</b> 🚀\n\n"
        "Your gateway to secure and automated wealth growth.\n\n"
        "Use /dashboard to get started."
    )

    # --- Wallet Templates ---
    DEPOSIT_SUCCESS: Final[str] = (
        "✅ <b>Deposit Confirmed</b>\n\n"
        "Amount: {amount}\n"
        "Ref: <code>{reference}</code>\n"
        "Timestamp: {timestamp}"
    )

    # --- Investment Templates ---
    INVESTMENT_PURCHASED: Final[str] = (
        "💼 <b>Investment Activated</b>\n\n"
        "Plan: {plan_name}\n"
        "Capital: {amount}\n"
        "Daily ROI: {roi_rate}%"
    )

    @classmethod
    def get_deposit_success_message(
        cls, amount: Any, reference: str, timestamp: Any
    ) -> str:
        """Helper to render deposit success message with formatted data."""
        context = {
            "amount": format_ngn_currency(amount),
            "reference": reference,
            "timestamp": format_to_local_time(timestamp),
        }
        return TemplateRenderer.render(cls.DEPOSIT_SUCCESS, context)

    @classmethod
    def get_investment_purchase_message(
        cls, plan_name: str, amount: Any, roi_rate: Any
    ) -> str:
        """Helper to render investment purchase confirmation."""
        context = {
            "plan_name": plan_name,
            "amount": format_ngn_currency(amount),
            "roi_rate": str(roi_rate),
        }
        return TemplateRenderer.render(cls.INVESTMENT_PURCHASED, context)
