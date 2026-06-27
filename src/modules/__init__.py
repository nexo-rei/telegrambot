# __init__.py
"""Domain Modules Root Registry.

This package acts as the central interface for all enterprise domain 
subsystems within the Nigerian Investment Platform. It exposes the public 
API surfaces of the modular architecture while strictly encapsulating internal 
implementation details to ensure loose coupling and architectural integrity.
"""

from typing import Final

# Package Metadata
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Public Module Namespace Exports
# Note: Lazy imports are preferred at the point of use to minimize startup 
# latency in the primary application entry point.
__all__: Final[list[str]] = [
    "authentication",
    "dashboard",
    "wallet",
    "deposits",
    "withdrawals",
    "transactions",
    "investment_plans",
    "active_investments",
    "daily_income",
    "referral_system",
    "referral_rewards",
    "gift_codes",
    "daily_check_in",
    "vip_levels",
    "notifications",
    "announcements",
    "support_tickets",
    "admin_panel",
    "moderators",
    "statistics",
    "analytics",
    "fraud_security",
    "logs",
    "audit_logs",
    "scheduler",
    "cron_jobs",
    "settings",
    "backup_system",
    "file_storage",
    "media_manager",
    "report_generation",
]
