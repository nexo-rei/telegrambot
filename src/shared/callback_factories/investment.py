# investment.py
"""UI Investment Callback Factory Primitives.

Defines the authoritative, strongly-typed `CallbackData` structures governing investment plan
selections, capital deployment confirmations, dynamic asset monitoring, and reinvestment actions.
Enforces validation guards and strict payload constraints to meet Telegram's wire transmission limits.
"""

import logging
from typing import Final, Optional
from aiogram.filters.callback_data import CallbackData

logger = logging.getLogger("investment_platform.shared.callbacks.investment")

# Strict wire architecture validation boundaries
MAX_INVEST_CALLBACK_BYTES: Final[int] = 64


class InvestmentCallback(CallbackData, prefix="inv_v2"):
    """Authoritative structural schema driving investment-related user interactions across layers."""
    
    action: str          # Contextual operation verb (e.g., "view_plan", "buy_confirm", "claim_yield", "history")
    plan_id: str = ""    # String token reference naming the underlying domain capital structure plan
    invest_id: str = ""  # Unique uuid token referencing an active operational user capital placement asset
    tx_id: str = ""      # Transaction tracking index reference matching the payment reconciliation core
    page: int = 0        # Page index tracker supporting tabular listing pagination panels

    @classmethod
    def create_safe(
        cls,
        action: str,
        plan_id: str = "",
        invest_id: str = "",
        tx_id: str = "",
        page: int = 0
    ) -> "InvestmentCallback":
        """Factory pattern constructor validating constraints prior to instantiating structural layouts.

        Args:
            action: Core operational pipeline command action tag.
            plan_id: Domain structural plan tracking key code identification string.
            invest_id: Unique record location index for user specific active portfolio assets.
            tx_id: Ledger allocation index mapping specific cash verification actions.
            page: Logical pagination number tracking horizontal menu segments.
        """
        if not action:
            raise ValueError("Invalid configuration: Investment operations require a declared context action key.")
            
        if page < 0:
            raise ValueError(f"Structural verification breach: Paging limits cannot use negative indices: {page}")

        # Construct and evaluate a simulated data frame string to guarantee physical platform safety boundaries
        simulated_data = f"inv_v2:{action}:{plan_id}:{invest_id}:{tx_id}:{page}"
        byte_len = len(simulated_data.encode("utf-8"))
        
        if byte_len > MAX_INVEST_CALLBACK_BYTES:
            error_msg = (
                f"Wire transport layout exception. Assembled investment string [{byte_len} bytes] "
                f"exceeds maximum allowed payload boundary ({MAX_INVEST_CALLBACK_BYTES} bytes): '{simulated_data}'"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        return cls(action=action, plan_id=plan_id, invest_id=invest_id, tx_id=tx_id, page=page)

    # --- Reusable Static Structural Domain Utility Builders ---

    @staticmethod
    def build_plan_view(plan_id: str) -> "InvestmentCallback":
        """Generates an explicit callback tracking blueprint to examine specialized operational parameters."""
        return InvestmentCallback.create_safe(action="view_plan", plan_id=plan_id)

    @staticmethod
    def build_purchase_confirmation(plan_id: str, estimated_tx_id: str) -> "InvestmentCallback":
        """Compiles standard authorization tokens confirming direct financial commitment to target yield tiers."""
        return InvestmentCallback.create_safe(action="buy_confirm", plan_id=plan_id, tx_id=estimated_tx_id)

    @staticmethod
    def build_yield_claim(active_portfolio_investment_id: str) -> "InvestmentCallback":
        """Generates capital asset collection tokens deployed straight to compounding micro-services."""
        return InvestmentCallback.create_safe(action="claim_yield", invest_id=active_portfolio_investment_id)
