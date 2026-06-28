"""Shared Financial Invariants Matrix.

BUG FIX: `FinancialValidationResult` dataclass used `Optional[str]` for `error_message`
but `Optional` was never imported from typing.
"""

from dataclasses import dataclass
from enum import Enum, unique
from typing import Final, Optional


# --- Core Currency Metrics ---
DEFAULT_CURRENCY_NAME: Final[str] = "Nigerian Naira"
DEFAULT_CURRENCY_CODE: Final[str] = "NGN"
DEFAULT_CURRENCY_SYMBOL: Final[str] = "₦"
DECIMAL_PRECISION: Final[int] = 2
THOUSANDS_SEPARATOR: Final[str] = ","
DECIMAL_SEPARATOR: Final[str] = "."


# --- Wallet Parameters ---
MIN_WALLET_BALANCE_NGN: Final[float] = 0.00
MAX_WALLET_BALANCE_NGN: Final[float] = 100_000_000.00
WALLET_PRECISION: Final[int] = 4
WALLET_CACHE_TTL_SECONDS: Final[int] = 60
WALLET_REFRESH_INTERVAL_SECONDS: Final[int] = 15


# --- Deposit Boundaries ---
MIN_DEPOSIT_AMOUNT_NGN: Final[float] = 1_000.00
MAX_DEPOSIT_AMOUNT_NGN: Final[float] = 10_000_000.00
DEPOSIT_PENDING_TIMEOUT_SECONDS: Final[int] = 7200   # 2 Hours
DEPOSIT_VERIFICATION_TIMEOUT_SECONDS: Final[int] = 86400  # 24 Hours
DEPOSIT_AUTO_EXPIRE_SECONDS: Final[int] = 7200
DAILY_DEPOSIT_LIMIT_NGN: Final[float] = 20_000_000.00
MONTHLY_DEPOSIT_LIMIT_NGN: Final[float] = 100_000_000.00


# --- Withdrawal Boundaries ---
MIN_WITHDRAWAL_AMOUNT_NGN: Final[float] = 2_000.00
MAX_WITHDRAWAL_AMOUNT_NGN: Final[float] = 5_000_000.00
WITHDRAWAL_PROCESSING_TIMEOUT_SECONDS: Final[int] = 172800  # 48 Hours
DAILY_WITHDRAWAL_LIMIT_NGN: Final[float] = 10_000_000.00
MONTHLY_WITHDRAWAL_LIMIT_NGN: Final[float] = 50_000_000.00
WITHDRAWAL_COOLDOWN_SECONDS: Final[int] = 86400  # 24 Hours between requests
MAX_PENDING_WITHDRAWALS_PER_USER: Final[int] = 1


# --- Investment Metrics ---
MIN_INVESTMENT_AMOUNT_NGN: Final[float] = 5_000.00
MAX_INVESTMENT_AMOUNT_NGN: Final[float] = 25_000_000.00
MIN_EXPECTED_ROI_PERCENTAGE: Final[float] = 0.5
MAX_EXPECTED_ROI_PERCENTAGE: Final[float] = 5.0
SUPPORTED_PLAN_DURATIONS_DAYS: Final[tuple[int, ...]] = (30, 60, 90, 180, 365)
DAILY_INCOME_CRON_TRIGGER_TIME: Final[str] = "00:00"  # UTC midnight payout execution
REINVESTMENT_DELAY_COOLDOWN_SECONDS: Final[int] = 300


# --- Network Referral Tree Parameters ---
MAX_REFERRAL_LEVELS_CAP: Final[int] = 3
REFERRAL_REWARD_PRECISION: Final[int] = 4
REFERRAL_CACHE_TTL_SECONDS: Final[int] = 300
REFERRAL_MUTATION_COOLDOWN_SECONDS: Final[int] = 60


# --- VIP Matrix Boundaries ---
MIN_VIP_LEVEL: Final[int] = 0
MAX_VIP_LEVEL: Final[int] = 5
VIP_UPGRADE_DELAY_SECONDS: Final[int] = 60


# --- Payment Gateway Integration Parameters ---
PAYMENT_SESSION_TIMEOUT_SECONDS: Final[int] = 1800  # 30 Minutes
PAYMENT_WEBHOOK_TIMEOUT_SECONDS: Final[int] = 30
PAYMENT_MAX_RETRY_LIMIT: Final[int] = 3
PAYMENT_RETRY_DELAY_SECONDS: Final[int] = 5
PAYMENT_VERIFICATION_INTERVAL_SECONDS: Final[int] = 10


@unique
class FinancialTransactionType(str, Enum):
    """Authoritative system classification ledger tokens for capital monitoring flows."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    INVESTMENT_EXECUTION = "INVESTMENT_EXECUTION"
    YIELD_ACCRUAL = "YIELD_ACCRUAL"
    REFERRAL_BONUS = "REFERRAL_BONUS"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT"


@dataclass(frozen=True)
class FinancialValidationResult:
    """Immutable data frame conveying structural outcome traces from validation checks."""
    is_valid: bool
    # BUG FIX: Optional was used but not imported. Added Optional to imports above.
    error_message: Optional[str] = None


# --- In-Line Structural Validation Helpers ---

def validate_deposit_bounds(amount: float) -> FinancialValidationResult:
    """Validates an inbound deposit amount against strict framework limits."""
    if amount < MIN_DEPOSIT_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount is below the minimum deposit entry barrier of ₦{MIN_DEPOSIT_AMOUNT_NGN:,.2f}.",
        )
    if amount > MAX_DEPOSIT_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount exceeds the maximum permissible single deposit allocation limit of ₦{MAX_DEPOSIT_AMOUNT_NGN:,.2f}.",
        )
    return FinancialValidationResult(is_valid=True)


def validate_withdrawal_bounds(amount: float, available_balance: float) -> FinancialValidationResult:
    """Checks an outbound liquidation request against limits and real-time ledger capacities."""
    if amount < MIN_WITHDRAWAL_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount is below the minimum capital extraction baseline of ₦{MIN_WITHDRAWAL_AMOUNT_NGN:,.2f}.",
        )
    if amount > MAX_WITHDRAWAL_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount exceeds the maximum single liquidation velocity limit of ₦{MAX_WITHDRAWAL_AMOUNT_NGN:,.2f}.",
        )
    if amount > available_balance:
        return FinancialValidationResult(
            is_valid=False,
            error_message="Insufficient available ledger balance to clear this withdrawal order allocation.",
        )
    return FinancialValidationResult(is_valid=True)


def validate_investment_bounds(amount: float, available_balance: float) -> FinancialValidationResult:
    """Validates asset acquisition bounds against the global plan distribution matrix."""
    if amount < MIN_INVESTMENT_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount is below the minimum allocation threshold for investment plans of ₦{MIN_INVESTMENT_AMOUNT_NGN:,.2f}.",
        )
    if amount > MAX_INVESTMENT_AMOUNT_NGN:
        return FinancialValidationResult(
            is_valid=False,
            error_message=f"Amount exceeds the maximum allocation threshold for investment plans of ₦{MAX_INVESTMENT_AMOUNT_NGN:,.2f}.",
        )
    if amount > available_balance:
        return FinancialValidationResult(
            is_valid=False,
            error_message="Insufficient wallet balance available to fund this capital expansion contract.",
        )
    return FinancialValidationResult(is_valid=True)
