# admin.py
"""UI Administrative Governance Callback Factory Primitives.

Defines the authoritative, strongly-typed `CallbackData` structures driving secure,
permissioned back-office control panels, operational workflows, and system state
mutations. Enforces validation rules and safety bounds to protect administrative
payload lines against Telegram's wire transmission limits.
"""

import logging
from typing import Final, Optional
from aiogram.filters.callback_data import CallbackData

logger = logging.getLogger("investment_platform.shared.callbacks.admin")

# Strict wire architecture validation boundaries
MAX_ADMIN_CALLBACK_BYTES: Final[int] = 64


class AdminCallback(CallbackData, prefix="adm_v2"):
    """Authoritative structural schema driving administrative management actions across layers."""

    action: str          # Targeted pipeline action verb (e.g., "dashboard", "usr_ban", "tx_approve", "sys_backup")
    module: str          # Target subdomain routing category (e.g., "users", "finance", "tickets", "system")
    target_id: str = ""   # Multi-purpose identifier string (e.g., user_id, transaction_id, ticket_id)
    page: int = 0        # Page index tracker supporting administrative tracking tabular views

    @classmethod
    def create_safe(
        cls,
        action: str,
        module: str,
        target_id: str = "",
        page: int = 0
    ) -> "AdminCallback":
        """Factory pattern constructor validating protocol payload rules prior to structural rendering.

        Args:
            action: Specific administrative operation verb.
            module: Core business logic module category target context.
            target_id: Entity database indexing primary reference code.
            page: Logical navigation page number index tracker.
        """
        if not action or not module:
            raise ValueError("Invalid configuration: Administrative callbacks require explicit action and module vectors.")

        if page < 0:
            raise ValueError(f"Structural verification breach: Administrative paging lists cannot utilize negative indices: {page}")

        # Assemble and monitor a simulated token line to guarantee wire safety threshold alignment
        simulated_data = f"adm_v2:{action}:{module}:{target_id}:{page}"
        byte_len = len(simulated_data.encode("utf-8"))

        if byte_len > MAX_ADMIN_CALLBACK_BYTES:
            error_msg = (
                f"Back-office transport blueprint boundary exception. Assembled administrative payload string [{byte_len} bytes] "
                f"exceeds maximum platform wire depth limit ({MAX_ADMIN_CALLBACK_BYTES} bytes): '{simulated_data}'"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        return cls(action=action, module=module, target_id=target_id, page=page)

    # --- Reusable Back-Office Operational Utility Builders ---

    @staticmethod
    def build_dashboard_root() -> "AdminCallback":
        """Generates the base core command path pointing back to the admin control panel root."""
        return AdminCallback.create_safe(action="dashboard", module="core")

    @staticmethod
    def build_user_action(operation_verb: str, selected_user_id: str) -> "AdminCallback":
        """Compiles targeted individual user structural modification command parameters."""
        return AdminCallback.create_safe(action=operation_verb, module="users", target_id=selected_user_id)

    @staticmethod
    def build_financial_reconciliation(verdict_action: str, ledger_tx_id: str) -> "AdminCallback":
        """Assembles atomic pipeline confirmation codes driving capital deposit/withdrawal releases."""
        return AdminCallback.create_safe(action=verdict_action, module="finance", target_id=ledger_tx_id)
