# datetime_utils.py
"""Enterprise Datetime and Chronological Coordination Utility.

Provides a robust, timezone-aware framework for handling temporal operations. 
Centralizes logic for UTC-to-Lagos conversion, investment maturity calculations, 
and human-readable duration formatting to ensure architectural consistency across 
the platform's scheduling and financial modules.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Final, Union, Optional

# Constants for centralized temporal governance
LAGOS_TZ: Final[ZoneInfo] = ZoneInfo("Africa/Lagos")
DEFAULT_DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def get_now_utc() -> datetime:
    """Returns the current UTC-aware datetime."""
    return datetime.now(timezone.utc)


def get_now_lagos() -> datetime:
    """Returns the current Africa/Lagos-aware datetime."""
    return datetime.now(LAGOS_TZ)


def format_to_local_time(dt: datetime, fmt: str = DEFAULT_DATETIME_FORMAT) -> str:
    """Converts a UTC datetime to Africa/Lagos time and formats as a string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LAGOS_TZ).strftime(fmt)


def seconds_until(target_dt: datetime) -> int:
    """Calculates the integer number of seconds remaining until the target datetime."""
    now = get_now_utc()
    delta = target_dt - now
    return max(int(delta.total_seconds()), 0)


def is_expired(target_dt: datetime) -> bool:
    """Determines if the provided target datetime has already passed."""
    return get_now_utc() > target_dt


def get_next_midnight() -> datetime:
    """Calculates the upcoming midnight in Africa/Lagos time."""
    now = get_now_lagos()
    next_day = now + timedelta(days=1)
    return next_day.replace(hour=0, minute=0, second=0, microsecond=0)


def calculate_investment_maturity(start_date: datetime, duration_days: int) -> datetime:
    """Calculates the exact maturity timestamp for an investment product."""
    return start_date + timedelta(days=duration_days)


def format_duration(seconds: int) -> str:
    """Formats raw seconds into a human-readable duration string."""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "Just now"


def safe_datetime(dt_input: Union[datetime, str, float]) -> Optional[datetime]:
    """Safely converts input types to a timezone-aware UTC datetime object."""
    try:
        if isinstance(dt_input, datetime):
            return dt_input.astimezone(timezone.utc) if dt_input.tzinfo else dt_input.replace(tzinfo=timezone.utc)
        if isinstance(dt_input, (float, int)):
            return datetime.fromtimestamp(dt_input, tz=timezone.utc)
        return datetime.fromisoformat(dt_input).astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None
