# screen_manager.py
"""UI Screen Management Subsystem.

Authoritative state coordinator and lifecycle engine for the platform's presentation
matrix. Orchestrates screen lookups, dynamic parameter state injections, asynchronous 
lifecycle hook execution, and structured state recovery pathways to ensure consistent 
navigation tracks across user interaction timelines.
"""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime, UTC
import logging
from typing import Any, Dict, Final, List, Optional, Type

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from src.ui_system.ui_manager import UIManager, RenderMode

logger = logging.getLogger("investment_platform.ui.screens")


class ScreenState:
    """Encapsulates runtime data profiles and trace vectors for an active screen session."""

    def __init__(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> None:
        self.chat_id: Final[int] = chat_id
        self.screen_key: Final[str] = screen_key
        self.params: Dict[str, Any] = params or {}
        self.message_id: Optional[int] = None
        self.registered_at: Final[datetime] = datetime.now(UTC)
        self.last_interaction_at: datetime = datetime.now(UTC)


class BaseScreen:
    """Abstract baseline class defining standard protocols for presentation components."""

    def __init__(self, key: str) -> None:
        self.key: Final[str] = key

    async def before_open(self, chat_id: int, params: Dict[str, Any]) -> None:
        """Executed immediately prior to dispatching layout instructions."""
        pass

    async def after_open(self, chat_id: int, state: ScreenState) -> None:
        """Executed immediately after layout statements complete successfully."""
        pass

    async def before_close(self, chat_id: int) -> None:
        """Executed prior to evicting layout from viewport contexts."""
        pass

    async def after_close(self, chat_id: int) -> None:
        """Executed post physical elimination of screen contexts."""
        pass

    async def before_refresh(self, chat_id: int, state: ScreenState) -> None:
        """Executed prior to performing state sync or string mutations."""
        pass

    async def after_refresh(self, chat_id: int, state: ScreenState) -> None:
        """Executed post completion of text adjustments."""
        pass

    async def build_content(self, chat_id: int, params: Dict[str, Any]) -> tuple[str, Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup]]:
        """Compiles structural layout tokens, returning formatted text and markup arrays."""
        raise NotImplementedError("Structural screen models must explicitly implement content compilation blocks.")


class ScreenManager:
    """Lifecycle controller enforcing operational integrity over runtime user viewports."""

    def __init__(self, ui_manager: UIManager) -> None:
        """Initializes the structural screen lifecycle framework.

        Args:
            ui_manager: Central layout rendering dependency driver.
        """
        self.ui_manager: Final[UIManager] = ui_manager
        self._registry: Dict[str, BaseScreen] = {}
        self._navigation_stacks: Dict[int, List[ScreenState]] = {}
        self._state_cache: Dict[int, ScreenState] = {}

    # --- Screen Central Registry Management ---

    def register_screen(self, screen: BaseScreen) -> None:
        """Binds a structural screen component directly into the executable layout grid."""
        if not screen or not screen.key:
            raise ValueError("Invalid screen implementation rejected by governance verification bounds.")
        self._registry[screen.key] = screen
        logger.debug(f"Screen component '{screen.key}' attached to operational grid registry.")

    def lookup_screen(self, screen_key: str) -> BaseScreen:
        """Locates an active screen layout block or raises descriptive route exceptions."""
        screen = self._registry.get(screen_key)
        if not screen:
            logger.error(f"Routing boundary violation. Screen descriptor key '{screen_key}' missing from context matrix.")
            raise KeyError(f"Target execution screen resource path not registered: '{screen_key}'")
        return screen

    def remove_screen(self, screen_key: str) -> bool:
        """Evicts a target descriptor path from the operational tracking registry."""
        return self._registry.pop(screen_key, None) is not None

    # --- Stateful Core Navigation Workflows ---

    async def open_screen(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Executes full lifecycle pathways to display a freshly requested structural view.

        Args:
            chat_id: Targeted individual customer chat identification index.
            screen_key: Authoritative lookup token identifying the structural layout target.
            params: Optional dict payloads conveying entity parameters or context variables.
        """
        try:
            screen = self.lookup_screen(screen_key)
            runtime_params = params or {}
            
            await screen.before_open(chat_id, runtime_params)
            
            text_payload, markup = await screen.build_content(chat_id, runtime_params)
            
            success = await self.ui_manager.execute_screen_render(
                chat_id=chat_id,
                screen_key=screen_key,
                text_payload=text_payload,
                reply_markup=markup,
                mode=RenderMode.AUTO
            )
            
            if success:
                ui_ctx = self.ui_manager.get_context(chat_id)
                new_state = ScreenState(chat_id, screen_key, runtime_params)
                new_state.message_id = ui_ctx.last_message_id
                
                if chat_id not in self._navigation_stacks:
                    self._navigation_stacks[chat_id] = []
                
                self._navigation_stacks[chat_id].append(new_state)
                self._state_cache[chat_id] = new_state
                
                await screen.after_open(chat_id, new_state)
                return True
                
            return False
        except Exception as error:
            logger.error(f"Failed handling structural route allocation step for screen '{screen_key}': {error}", exc_info=True)
            return await self._handle_recovery_fallback(chat_id)

    async def replace_screen(self, chat_id: int, screen_key: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Swaps the latest active viewport layout tracking frame directly without growing history limits."""
        stack = self._navigation_stacks.get(chat_id, [])
        if stack:
            current_state = stack.pop()
            screen = self._registry.get(current_state.screen_key)
            if screen:
                await screen.before_close(chat_id)
                await screen.after_close(chat_id)
                
        return await self.open_screen(chat_id, screen_key, params)

    async def refresh_screen(self, chat_id: int) -> bool:
        """Triggers sync execution arrays on active screens, executing matching lifecycle hooks."""
        state = self._state_cache.get(chat_id)
        if not state:
            return await self.open_screen(chat_id, "HOME")
            
        try:
            screen = self.lookup_screen(state.screen_key)
            state.last_interaction_at = datetime.now(UTC)
            
            await screen.before_refresh(chat_id, state)
            
            text_payload, markup = await screen.build_content(chat_id, state.params)
            success = await self.ui_manager.execute_screen_render(
                chat_id=chat_id,
                screen_key=state.screen_key,
                text_payload=text_payload,
                reply_markup=markup,
                mode=RenderMode.EDIT_EXISTING
            )
            
            if success:
                await screen.after_refresh(chat_id, state)
                return True
            return False
        except Exception as error:
            logger.error(f"Error encountered updating active structural view frame {state.screen_key}: {error}")
            return await self._handle_recovery_fallback(chat_id)

    async def return_to_previous(self, chat_id: int) -> bool:
        """Evicts local frames from stack tracks to drop back into upstream screen structures."""
        stack = self._navigation_stacks.get(chat_id, [])
        if len(stack) <= 1:
            return await self.open_screen(chat_id, "HOME")
            
        # Evict current layout tracking footprint
        active_state = stack.pop()
        active_screen = self._registry.get(active_state.screen_key)
        if active_screen:
            await active_screen.before_close(chat_id)
            await active_screen.after_close(chat_id)
            
        # Extract direct predecessor state layout vectors
        previous_state = stack.pop()
        return await self.open_screen(chat_id, previous_state.screen_key, previous_state.params)

    async def return_to_home(self, chat_id: int) -> bool:
        """Flushes stack history arrays cleanly, resetting the root view back to Home profiles."""
        stack = self._navigation_stacks.get(chat_id, [])
        for state in reversed(stack):
            screen = self._registry.get(state.screen_key)
            if screen:
                await screen.before_close(chat_id)
                await screen.after_close(chat_id)
                
        self._navigation_stacks[chat_id] = []
        self._state_cache.pop(chat_id, None)
        return await self.open_screen(chat_id, "HOME")

    # --- Structural Session Invalidation & Error Recovery ---

    async def _handle_recovery_fallback(self, chat_id: int) -> bool:
        """Safely catches routing drops, dropping users back onto stable base interfaces."""
        logger.warning(f"Executing emergency interface stabilization routing for customer footprint {chat_id}.")
        try:
            self._navigation_stacks[chat_id] = []
            self._state_cache.pop(chat_id, None)
            
            # Simple direct injection structure fallback profile content bypass
            fallback_text = (
                "┏━━━━━━━━━━━━━━━━━━━━┓\n"
                "⚠️ <b>SYSTEM CORRECTION BOUNDARY</b>\n"
                "┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "An operational screen layout mutation boundary trace was interrupted.\n"
                "Your interface navigation tracking layers have been stabilized safely."
            )
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardMarkup.button(text="🔄 Return to Safety Core", callback_data="ui_navigate_home")
            ]])
            
            return await self.ui_manager.execute_screen_render(
                chat_id=chat_id,
                screen_key="FALLBACK_RECOVERY",
                text_payload=fallback_text,
                reply_markup=markup,
                mode=RenderMode.FORCE_NEW
            )
        except Exception as critical_fault:
            logger.critical(f"Total collapse encountered running crash containment pathways on {chat_id}: {critical_fault}")
            return False

    def clear_stale_cache(self, retention_seconds: int = 3600) -> None:
        """Prunes historical tracking allocations exceeding max temporal boundaries to save memory."""
        now = datetime.now(UTC)
        eviction_keys = []
        
        for chat_id, state in self._state_cache.items():
            if (now - state.last_interaction_at).total_seconds() > retention_seconds:
                eviction_keys.append(chat_id)
                
        for chat_id in eviction_keys:
            self._navigation_stacks.pop(chat_id, None)
            self._state_cache.pop(chat_id, None)
            
        if eviction_keys:
            logger.info(f"Memory sweep complete. Evicted {len(eviction_keys)} stale navigation stacks from cache.")
