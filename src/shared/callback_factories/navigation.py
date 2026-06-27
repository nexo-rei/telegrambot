# navigation.py
"""UI Navigation Callback Factory Primitives.

Defines the authoritative, strongly-typed `CallbackData` structures governing global 
navigation transitions, structural page allocations, and explicit multi-tenant parameters.
Enforces static schema rules and size bounds to guarantee wire compliance with 
Telegram's data limits.
"""

import logging
from typing import Any, Final, Optional
from aiogram.filters.callback_data import CallbackData

logger = logging.getLogger("investment_platform.shared.callbacks.navigation")

# Strict wire architecture validation boundaries
MAX_ROUTE_BYTES: Final[int] = 64


class NavigationCallback(CallbackData, prefix="nav_v2"):
    """Authoritative structural schema driving asynchronous view transit actions across layers."""
    
    action: str        # Fundamental transition verb (e.g., "open", "back", "page", "home")
    target: str        # Structural screen descriptor identifier destination string code
    page: int = 0      # Logical payload paging value matrix tracking coordinate position
    payload: str = ""  # Ephemeral context tracking argument payload compressed token string

    @classmethod
    def create_safe(
        cls, 
        action: str, 
        target: str, 
        page: int = 0, 
        payload: str = ""
    ) -> "NavigationCallback":
        """Factory pattern constructor validating input length properties prior to compilation.

        Args:
            action: Primary routing operational action key.
            target: Absolute destination identifier tag name.
            page: Sequence index tracker (must be non-negative).
            payload: Auxiliary metadata string appended into the callback structure.
        """
        # Enforce baseline structure checks at compilation points
        if not action or not target:
            raise ValueError("Invalid parameters: Callback boundaries require populated action and target tokens.")
            
        if page < 0:
            raise ValueError(f"Structural verification breach: Page parameter cannot be negative: {page}")

        # Assemble temporary mock string to verify compliance with structural transport ceilings
        simulated_data = f"nav_v2:{action}:{target}:{page}:{payload}"
        byte_len = len(simulated_data.encode("utf-8"))
        
        if byte_len > MAX_ROUTE_BYTES:
            error_msg = (
                f"Wire layout specification limit crossed. Assembled tracking string "
                f"[{byte_len} bytes] exceeds maximum safe capacity ({MAX_ROUTE_BYTES} bytes): '{simulated_data}'"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        return cls(action=action, target=target, page=page, payload=payload)

    # --- Reusable Static Utility Builders ---

    @staticmethod
    def build_home_callback() -> "NavigationCallback":
        """Generates a standard navigation callback for returning to the root home matrix."""
        return NavigationCallback.create_safe(action="home", target="HOME")

    @staticmethod
    def build_back_callback(current_screen: str) -> "NavigationCallback":
        """Generates a standard back-navigation callback relative to the current viewport tracking line."""
        return NavigationCallback.create_safe(action="back", target=current_screen)

    @staticmethod
    def build_page_swap(target_screen: str, destination_page: int) -> "NavigationCallback":
        """Generates a paginated transition matrix callback targeting specific data layouts."""
        return NavigationCallback.create_safe(action="page", target=target_screen, page=destination_page)
