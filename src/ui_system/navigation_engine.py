# navigation_engine.py
"""UI Stateful Navigation Engine.

Authoritative deep-routing matrix and security transit guard for user interfaces.
Coordinates structural viewport transitions, deep-linking contracts, multi-tier
permission guard clearances, and protective history stack depth ceilings.
"""

from collections.abc import Callable, Coroutine
from datetime import datetime, UTC
import logging
from typing import Any, Dict, Final, List, Optional

from src.ui_system.screen_manager import ScreenManager, ScreenState

logger = logging.getLogger("investment_platform.ui.navigation")

# Configuration Limits
MAX_STACK_DEPTH_CEILING: Final[int] = 15


class RouteGuardError(Exception):
    """Raised when navigation fails route or authorization constraints."""
    pass


class NavigationEngine:
    """Enterprise stateful routing manager supervising layout stack mutations."""

    def __init__(self, screen_manager: ScreenManager) -> None:
        """Initializes the navigation routing controller.

        Args:
            screen_manager: Core lifecycle engine for layout management.
        """
        self.screen_manager: Final[ScreenManager] = screen_manager
        self._route_guards: Dict[str, List[Callable[[int, Dict[str, Any]], Coroutine[Any, Any, bool]]]] = {}
        self._deep_link_registry: Dict[str, str] = {}

    # --- Structural Security Route Guards Registration ---

    def register_guard(self, screen_key: str, guard_callable: Callable[[int, Dict[str, Any]], Coroutine[Any, Any, bool]]) -> None:
        """Applies a custom asynchronous permission checking interceptor to a named route."""
        if screen_key not in self._route_guards:
            self._route_guards[screen_key] = []
        self._route_guards[screen_key].append(guard_callable)
        logger.debug(f"Route security guard appended successfully to destination key: '{screen_key}'")

    def register_deep_link(self, dynamic_prefix: str, matching_screen_key: str) -> None:
        """Maps an internal path handler alias directly to an explicit target view resource."""
        self._deep_link_registry[dynamic_prefix.strip().lower()] = matching_screen_key

    async def _evaluate_route_clearance(self, chat_id: int, screen_key: str, params: Dict[str, Any]) -> bool:
        """Evaluates registered structural guards sequentially prior to advancing view states."""
        guards = self._route_guards.get(screen_key, [])
        for guard in guards:
            try:
                cleared = await guard(chat_id, params)
                if not cleared:
                    logger.warning(f"Navigation request rejected by security guard for chat index {chat_id} on route '{screen_key}'")
                    return False
            except Exception as guard_fault:
                logger.error(f"Critical execution failure inside guard evaluator sequence on route '{screen_key}': {guard_fault}")
                return False
        return True

    # --- Core Routing Operations API ---

    async def navigate_to(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigates to a specific screen, automatically validating state and permission rules.

        Args:
            chat_id: Unique individual user network location context.
            screen_key: Token string naming the destination layout target.
            params: Dictionary containing context data parameters.
        """
        runtime_params = params or {}
        
        # Enforce administrative and session state constraints before layout processing
        if not await self._evaluate_route_clearance(chat_id, screen_key, runtime_params):
            return await self.redirect_to(chat_id, "UNAUTHORIZED_ACCESS_LOCK", {"attempted_target": screen_key})

        # Protect against excessive stack memory allocations
        stack = self.screen_manager._navigation_stacks.get(chat_id, [])
        if len(stack) >= MAX_STACK_DEPTH_CEILING:
            logger.warning(f"Stack overflow boundary crossed for user identification branch {chat_id}. Condensing stack history frames.")
            if len(stack) > 1:
                # Evict oldest element while maintaining contemporary tracking layers
                stack.pop(0)

        logger.info(f"Routing user viewport session {chat_id} sequentially to route: '{screen_key}'")
        return await self.screen_manager.open_screen(chat_id, screen_key, runtime_params)

    async def replace_current(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Replaces the active screen frame directly, skipping historical backtracking logs."""
        runtime_params = params or {}
        if not await self._evaluate_route_clearance(chat_id, screen_key, runtime_params):
            return await self.redirect_to(chat_id, "UNAUTHORIZED_ACCESS_LOCK", {"attempted_target": screen_key})

        logger.info(f"Executing viewport substitution swap on identity track {chat_id} to route: '{screen_key}'")
        return await self.screen_manager.replace_screen(chat_id, screen_key, runtime_params)

    async def redirect_to(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Forces an absolute, context-free redirection pathway across layout frames."""
        logger.info(f"Forcing administrative redirection track on subscriber footprint {chat_id} straight to: '{screen_key}'")
        return await self.screen_manager.replace_screen(chat_id, screen_key, params)

    async def navigate_back(self, chat_id: int) -> bool:
        """Steps back one level in the viewport history stack chain."""
        logger.info(f"Processing back-navigation command layout requests for chat tracking line {chat_id}")
        return await self.screen_manager.return_to_previous(chat_id)

    async def navigate_home(self, chat_id: int) -> bool:
        """Flushes historical stack allocations completely and restores the home view profile."""
        logger.info(f"Resetting interface structural footprints to root home layouts for participant context {chat_id}")
        return await self.screen_manager.return_to_home(chat_id)

    async def refresh_current(self, chat_id: int) -> bool:
        """Triggers dynamic state refresh cycles directly on active screens."""
        logger.debug(f"Executing explicit refresh sequence matching viewport trace requirements for chat identifier {chat_id}")
        return await self.screen_manager.refresh_screen(chat_id)

    # --- Deep-Linking Integration Vectors ---

    async def resolve_deep_link(self, chat_id: int, deep_link_payload: str) -> bool:
        """Parses deep-linking payloads to map incoming tokens directly to target interfaces.

        Args:
            chat_id: Destination subscriber account verification reference index.
            deep_link_payload: Explicit text parameter extracted directly from start query tokens.
        """
        if not deep_link_payload:
            return await self.navigate_home(chat_id)

        sanitized_token = deep_link_payload.strip().lower()
        logger.info(f"Evaluating deep link inbound parameter string token layout sequence: '{sanitized_token}' for {chat_id}")

        # Handle parameterized patterns (e.g., ref_code, plan_id)
        if "_" in sanitized_token:
            prefix, argument = sanitized_token.split("_", 1)
            target_route = self._deep_link_registry.get(prefix)
            if target_route:
                return await self.navigate_to(chat_id, target_route, {"deep_link_argument": argument})

        # Handle direct structural layout conversions
        target_route = self._deep_link_registry.get(sanitized_token)
        if target_route:
            return await self.navigate_to(chat_id, target_route)

        # Default fallback route assignment when mapping logic cannot match payloads
        logger.warning(f"Unable to match deep link token '{sanitized_token}' against known routing tables. Defaulting to home.")
        return await self.navigate_to(chat_id, "HOME", {"unresolved_deep_link": deep_link_payload})
