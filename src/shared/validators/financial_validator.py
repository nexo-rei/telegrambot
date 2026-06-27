"""Production-Grade Financial Validation Engine.

Provides the centralized authorization and constraints-checking layer for all
monetary operations across the platform. Validates transaction boundaries, 
wallet states, and eligibility criteria for deposits, withdrawals, and 
investments to ensure system-wide financial integrity.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional

from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.shared.validators.financial_validator")


@dataclass(frozen=True)
class ValidationResult:
    """Standardized outcome for a financial validation request."""
    is_valid: bool
    error_code: Optional[str] = None
    message: Optional[str] = None


class ValidationError(Exception):
    """Custom exception for structured validation failures."""
    def __init__(self, message: str, code: str) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class FinancialValidator:
    """Centralized engine for validating financial constraints and business logic."""

    # Business Constraints
    MIN_DEPOSIT: Final[Decimal] = Decimal("1000.00")
    MAX_DEPOSIT: Final[Decimal] = Decimal("5000000.00")
    MIN_WITHDRAWAL: Final[Decimal] = Decimal("2000.00")

    async def validate_deposit(self, amount: Decimal) -> ValidationResult:
        """Validates deposit boundaries for NGN transactions."""
        if not PrecisionMath.is_positive(amount):
            return ValidationResult(False, "INVALID_AMOUNT", "Deposit amount must be positive.")
        
        if amount < self.MIN_DEPOSIT:
            return ValidationResult(False, "BELOW_MIN_DEPOSIT", f"Minimum deposit is {self.MIN_DEPOSIT} NGN.")
            
        if amount > self.MAX_DEPOSIT:
            return ValidationResult(False, "ABOVE_MAX_DEPOSIT", f"Maximum deposit is {self.MAX_DEPOSIT} NGN.")
            
        return ValidationResult(True)

    async def validate_withdrawal(
        self, amount: Decimal, wallet_balance: Decimal
    ) -> ValidationResult:
        """Validates withdrawal eligibility against wallet liquidity."""
        if amount < self.MIN_WITHDRAWAL:
            return ValidationResult(False, "BELOW_MIN_WITHDRAWAL", f"Minimum withdrawal is {self.MIN_WITHDRAWAL} NGN.")
            
        if amount > wallet_balance:
            return ValidationResult(False, "INSUFFICIENT_FUNDS", "Insufficient wallet balance for this withdrawal.")
            
        return ValidationResult(True)

    async def validate_investment_eligibility(
        self, amount: Decimal, wallet_balance: Decimal, plan_min: Decimal
    ) -> ValidationResult:
        """Checks if a user has sufficient funds to participate in an investment plan."""
        if amount < plan_min:
            return ValidationResult(False, "PLAN_MIN_NOT_MET", f"Investment below plan requirement of {plan_min} NGN.")
            
        if amount > wallet_balance:
            return ValidationResult(False, "INSUFFICIENT_FUNDS", "Insufficient balance for this investment.")
            
        return ValidationResult(True)
