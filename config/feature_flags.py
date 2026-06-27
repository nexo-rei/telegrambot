# feature_flags.py
"""Feature Flags Configuration Engine.

Consolidates, parses, and manages systemic feature flags dynamically across
the platform, allowing instant toggling of operational domains, payment structures,
and risk parameters without application code modification.
"""

from dataclasses import dataclass, field
from typing import Any, Dict
from config.base import settings


@dataclass
class FeatureFlags:
    """Production-grade feature toggling framework matrix.
    
    Coordinates the explicit runtime visibility parameters of modules, ensuring
    fail-safe containment of operational paths for the Nigerian NGN deployment.
    """

    # --- General Environment Operational States ---
    DEBUG: bool = field(default=settings.flags.DEBUG)
    DEVELOPMENT_MODE: bool = field(default=settings.flags.DEBUG)
    MAINTENANCE_MODE: bool = field(default=False)

    # --- Bot Communication Layer Matrix ---
    ENABLE_POLLING: bool = field(default=not settings.flags.ENABLE_WEBHOOK)
    ENABLE_WEBHOOK: bool = field(default=settings.flags.ENABLE_WEBHOOK)
    ENABLE_STARTUP_MESSAGE: bool = field(default=True)
    ENABLE_SHUTDOWN_MESSAGE: bool = field(default=True)

    # --- Localized Transactional Processing Gateways ---
    ENABLE_PAYSTACK: bool = field(default=True)
    ENABLE_FLUTTERWAVE: bool = field(default=False)  # Future-ready container
    ENABLE_DEPOSITS: bool = field(default=True)
    ENABLE_WITHDRAWALS: bool = field(default=True)
    ENABLE_MANUAL_APPROVAL: bool = field(default=True)  # Safe human validation step

    # --- core Investment Domain Capabilities ---
    ENABLE_INVESTMENTS: bool = field(default=True)
    ENABLE_DAILY_PROFIT: bool = field(default=True)
    ENABLE_REFERRALS: bool = field(default=True)
    ENABLE_GIFT_CODES: bool = field(default=True)
    ENABLE_DAILY_CHECKIN: bool = field(default=True)
    ENABLE_VIP_SYSTEM: bool = field(default=True)

    # --- Systemic Governance Interfaces ---
    ENABLE_ADMIN_PANEL: bool = field(default=True)
    ENABLE_ADMIN_LOGS: bool = field(default=True)
    ENABLE_BROADCASTS: bool = field(default=True)

    # --- Automated Security Perimeter Protection Controls ---
    ENABLE_RATE_LIMITER: bool = field(default=True)
    ENABLE_ANTI_SPAM: bool = field(default=True)
    ENABLE_FRAUD_DETECTION: bool = field(default=True)
    ENABLE_AUDIT_LOGS: bool = field(default=True)

    # --- Asynchronous Worker Background Management Processes ---
    ENABLE_SCHEDULER: bool = field(default=settings.flags.ENABLE_SCHEDULER)
    ENABLE_CRON: bool = field(default=True)
    ENABLE_BACKUPS: bool = field(default=settings.flags.ENABLE_BACKUP)

    # --- Media Processing and Document Extraction Engines ---
    ENABLE_MEDIA_STORAGE: bool = field(default=True)
    ENABLE_REPORT_GENERATION: bool = field(default=True)

    # --- Platform Telemetry Verification Framework ---
    ENABLE_HEALTH_CHECKS: bool = field(default=True)
    ENABLE_LOGGING: bool = field(default=True)

    def is_enabled(self, flag_name: str) -> bool:
        """Determines whether a specific system flag parameter is active.

        Args:
            flag_name: The target string attribute key to look up.

        Returns:
            bool: Representing the current boolean evaluation state.
        """
        return getattr(self, flag_name, False)

    def enable(self, flag_name: str) -> None:
        """Forces an targeted structural component online in memory dynamically.

        Args:
            flag_name: The attribute identifier key to alter.
        """
        if hasattr(self, flag_name):
            setattr(self, flag_name, True)

    def disable(self, flag_name: str) -> None:
        """Forces an targeted structural component offline in memory dynamically.

        Args:
            flag_name: The attribute identifier key to alter.
        """
        if hasattr(self, flag_name):
            setattr(self, flag_name, False)

    def get_all_flags_manifest(self) -> Dict[str, bool]:
        """Compiles a complete systemic status mapping schema of all toggles.

        Returns:
            Dict[str, bool]: Key-Value lookup frame tracking runtime permissions.
        """
        return {
            key: value for key, value in self.__dict__.items() 
            if isinstance(value, bool)
        }


# Export a singular thread-safe runtime instance tracking state memory configurations
feature_flags: FeatureFlags = FeatureFlags()
