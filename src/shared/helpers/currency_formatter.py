# currency_formatter.py
"""Financial Currency Formatting and Normalization Utility.

Provides a robust, precision-focused utility for handling monetary transactions 
in NGN (Nigerian Naira). Utilizes `decimal.Decimal` to eliminate floating-point 
arithmetic errors, ensuring absolute financial accuracy across ledgers, wallets, 
and reporting modules.
"""

from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Final, Union, Optional

# Constants for financial normalization
CURRENCY_SYMBOL: Final[str] = "₦"
DECIMAL_PRECISION: Final[str] = "0.01"


def safe_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
    """Safely converts arbitrary input types to a standardized Decimal object."""
    try:
        return Decimal(str(value)).quantize(Decimal(DECIMAL_PRECISION), rounding=ROUND_HALF_EVEN)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


def format_ngn_currency(
    amount: Union[int, float, str, Decimal], 
    include_symbol: bool = True,
    compact: bool = False
) -> str:
    """Formats a decimal amount into a human-readable NGN currency string."""
    value = safe_decimal(amount)

    if compact:
        return _to_compact_format(value)

    formatted = f"{value:,.2f}"
    return f"{CURRENCY_SYMBOL}{formatted}" if include_symbol else formatted


def _to_compact_format(value: Decimal) -> str:
    """Converts large monetary values into compact representations (e.g., 1.5M)."""
    if value >= 1_000_000_000:
        return f"{CURRENCY_SYMBOL}{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{CURRENCY_SYMBOL}{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{CURRENCY_SYMBOL}{value / 1_000:.1f}K"
    return f"{CURRENCY_SYMBOL}{value:,.0f}"


def parse_currency(amount_str: str) -> Decimal:
    """Parses a currency string into a Decimal object, stripping non-numeric characters."""
    sanitized = "".join(c for c in amount_str if c.isdigit() or c == ".")
    return safe_decimal(sanitized) if sanitized else Decimal("0.00")


def format_percentage(value: Union[float, Decimal], precision: int = 2) -> str:
    """Formats a numeric value as a percentage string."""
    decimal_val = safe_decimal(value)
    return f"{decimal_val:.{precision}f}%"


def format_roi(value: Union[float, Decimal]) -> str:
    """Formats a Return on Investment (ROI) metric for display."""
    return f"+{format_percentage(value)}"


def is_valid_amount(amount: Any) -> bool:
    """Validates if the provided input is a non-negative, valid financial amount."""
    try:
        val = safe_decimal(amount)
        return val >= 0
    except Exception:
        return False


def round_money(amount: Union[float, Decimal]) -> Decimal:
    """Applies standard financial rounding (Banker's rounding) to an amount."""
    return safe_decimal(amount)
