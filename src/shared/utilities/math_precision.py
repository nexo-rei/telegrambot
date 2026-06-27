# math_precision.py
"""Production-Grade Financial Arithmetic Utility.

Provides a robust, centralized engine for high-precision monetary calculations 
using Python's decimal.Decimal module. Ensures consistent, IEEE 754-compliant 
arithmetic for investments, ROI distributions, and referral commissions, 
eliminating floating-point inaccuracies typical in financial applications.
"""

import logging
from decimal import Decimal, ROUND_HALF_EVEN, getcontext, InvalidOperation
from typing import Final, Union

logger = logging.getLogger("investment_platform.shared.utilities.math_precision")

# Configure global Decimal context for financial standard
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_EVEN

class PrecisionError(Exception):
    """Base exception for mathematical and precision-related errors."""
    pass

class PrecisionMath:
    """Utility class for safe, high-precision financial operations."""

    DEFAULT_PRECISION: Final[int] = 2

    @staticmethod
    def safe_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
        """Converts arbitrary numeric inputs into a sanitized Decimal object."""
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            logger.error(f"Invalid numeric input for conversion: {value}")
            raise PrecisionError(f"Cannot convert {value} to Decimal") from e

    @classmethod
    def add(cls, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        return cls.safe_decimal(a) + cls.safe_decimal(b)

    @classmethod
    def subtract(cls, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        return cls.safe_decimal(a) - cls.safe_decimal(b)

    @classmethod
    def multiply(cls, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        return cls.safe_decimal(a) * cls.safe_decimal(b)

    @classmethod
    def divide(cls, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        divisor = cls.safe_decimal(b)
        if divisor == 0:
            raise PrecisionError("Division by zero in financial calculation.")
        return cls.safe_decimal(a) / divisor

    @classmethod
    def calculate_percentage(
        cls, amount: Union[int, float, str, Decimal], rate: Union[int, float, str, Decimal]
    ) -> Decimal:
        """Calculates a percentage of an amount."""
        amount_dec = cls.safe_decimal(amount)
        rate_dec = cls.safe_decimal(rate)
        return (amount_dec * rate_dec) / Decimal("100")

    @classmethod
    def calculate_roi(
        cls, capital: Union[int, float, str, Decimal], roi_rate: Union[int, float, str, Decimal]
    ) -> Decimal:
        """Computes periodic ROI for an investment."""
        return cls.calculate_percentage(capital, roi_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_EVEN
        )

    @classmethod
    def is_positive(cls, value: Union[int, float, str, Decimal]) -> bool:
        """Verifies if an amount is greater than zero."""
        return cls.safe_decimal(value) > 0

    @classmethod
    def compare_amounts(
        cls, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]
    ) -> int:
        """Returns 1 if a > b, -1 if a < b, 0 if equal."""
        val_a, val_b = cls.safe_decimal(a), cls.safe_decimal(b)
        if val_a > val_b: return 1
        if val_a < val_b: return -1
        return 0
