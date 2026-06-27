# keyboards.py
"""Production-grade Investment Plan Keyboard Builder.

Provides a centralized factory for constructing premium, fintech-style Telegram 
navigation interfaces for the investment product catalog. Implements modular 
builders for plan browsing, yield evaluation, and purchase confirmation workflows.
"""

from typing import Final, List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.investment_plans.dtos import InvestmentPlanDTO


class InvestmentPlanKeyboards:
    """Factory for generating highly responsive investment plan navigation keyboards."""

    @staticmethod
    def get_plans_list_keyboard(plans: List[InvestmentPlanDTO]) -> InlineKeyboardMarkup:
        """Generates a dynamic list of available investment plans."""
        builder = InlineKeyboardBuilder()
        for plan in plans:
            builder.button(
                text=f"💠 {plan.name} ({plan.roi_percentage}%)", 
                callback_data=f"plan_view_{plan.plan_id}"
            )
        builder.button(text="⬅️ Back to Dashboard", callback_data="nav_home")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_plan_details_keyboard(plan_id: str) -> InlineKeyboardMarkup:
        """Generates navigation for specific investment plan actions."""
        builder = InlineKeyboardBuilder()
        builder.button(text="💰 Invest Now", callback_data=f"plan_purchase_{plan_id}")
        builder.button(text="⬅️ Back to Plans", callback_data="nav_plans")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_purchase_confirmation_keyboard(plan_id: str) -> InlineKeyboardMarkup:
        """Generates final purchase confirmation and cancellation controls."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Confirm Purchase", callback_data=f"confirm_purchase_{plan_id}")
        builder.button(text="❌ Cancel", callback_data="nav_plans")
        builder.adjust(1)
        return builder.as_markup()
