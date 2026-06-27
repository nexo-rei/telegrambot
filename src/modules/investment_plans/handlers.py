# handlers.py
"""Production-grade Investment Plan Handlers.

Defines the Telegram update controllers for the investment plans module. Manages 
user interaction flows for browsing available investment products, viewing 
detailed yield metrics, and executing purchase requests. Delegates all core 
business logic to the InvestmentPlanService.
"""

import logging
from typing import Final

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.modules.investment_plans.services import InvestmentPlanService
from src.modules.investment_plans.keyboards import InvestmentPlanKeyboards

logger = logging.getLogger("investment_platform.modules.investment_plans.handlers")

router = Router(name="investment_plan_handlers")


@router.callback_query(F.data == "nav_plans")
async def handle_browse_plans(
    callback: CallbackQuery, service: InvestmentPlanService
) -> None:
    """Displays the list of available investment products."""
    try:
        plans = await service.get_all_active_plans()
        await callback.message.edit_text(
            "📈 *Available Investment Plans*\n\n"
            "Select a plan to view details and start earning:",
            reply_markup=InvestmentPlanKeyboards.get_plans_list_keyboard(plans),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching investment plans: {e}")
        await callback.answer("Unable to load investment plans.", show_alert=True)


@router.callback_query(F.data.startswith("plan_view_"))
async def handle_view_plan_details(
    callback: CallbackQuery, service: InvestmentPlanService
) -> None:
    """Displays comprehensive details for a selected investment plan."""
    plan_id = callback.data.replace("plan_view_", "")
    
    try:
        plan = await service.get_plan_details(plan_id)
        await callback.message.edit_text(
            f"💠 *Plan: {plan.name}*\n\n"
            f"ROI: {plan.roi_percentage}%\n"
            f"Duration: {plan.duration_days} days\n"
            f"Min Investment: ₦{plan.min_amount:,.2f}\n\n"
            "Would you like to invest in this plan?",
            reply_markup=InvestmentPlanKeyboards.get_plan_details_keyboard(plan_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error viewing plan {plan_id}: {e}")
        await callback.answer("Could not retrieve plan details.", show_alert=True)


@router.callback_query(F.data.startswith("plan_purchase_"))
async def handle_purchase_plan(
    callback: CallbackQuery, service: InvestmentPlanService, state: FSMContext
) -> None:
    """Initiates the purchase workflow for a specific plan."""
    plan_id = callback.data.replace("plan_purchase_", "")
    
    # Logic delegation to service for pre-purchase validation
    is_eligible = await service.validate_purchase_eligibility(callback.from_user.id, plan_id)
    
    if not is_eligible:
        await callback.answer("You are not eligible for this plan.", show_alert=True)
        return

    await state.update_data(selected_plan_id=plan_id)
    await callback.message.edit_text(
        "💰 *Confirm Investment*\n\n"
        "Proceed with purchase using your available wallet balance?",
        reply_markup=InvestmentPlanKeyboards.get_purchase_confirmation_keyboard(plan_id),
        parse_mode="Markdown"
    )
