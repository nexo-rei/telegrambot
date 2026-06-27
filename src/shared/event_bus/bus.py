# bus.py
"""Asynchronous Domain Event Bus.

Provides a decoupled communication backbone for the enterprise architecture. Enables
modules to trigger and listen for domain-specific events without direct coupling,
ensuring high modularity, testability, and operational flexibility across disparate
services like financial ledgers, notifications, and analytics pipelines.
"""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any, Final, Optional

logger = logging.getLogger("investment_platform.shared.event_bus")


class EventBus:
    """Centralized asynchronous message orchestrator for domain event propagation."""

    def __init__(self) -> None:
        """Initializes internal event-to-handler lookup registry."""
        self._handlers: Final[defaultdict[str, list[Callable[..., Coroutine[Any, Any, None]]]]] = defaultdict(list)
        self._lock: Final[asyncio.Lock] = asyncio.Lock()

    async def subscribe(
        self, 
        event_type: str, 
        handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> None:
        """Registers an asynchronous event listener for a specific domain event type."""
        async with self._lock:
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)
                logger.debug(f"Registered subscriber for event type: '{event_type}'")

    async def unsubscribe(
        self, 
        event_type: str, 
        handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> None:
        """Removes a previously registered event listener."""
        async with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unregistered subscriber from event type: '{event_type}'")

    async def publish(self, event_type: str, **payload: Any) -> None:
        """Dispatches an event payload to all registered subscribers asynchronously.

        Args:
            event_type: The domain event category tag.
            payload: Keyword arguments containing event data metrics.
        """
        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug(f"No active subscribers found for event: '{event_type}'")
            return

        tasks = [self._invoke_handler(handler, event_type, payload) for handler in handlers]
        
        # Execute handlers concurrently while ensuring individual failures do not block the chain
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _invoke_handler(
        self, 
        handler: Callable[..., Coroutine[Any, Any, None]], 
        event_type: str, 
        payload: dict[str, Any]
    ) -> None:
        """Executes individual handler logic wrapped in resilience exception handling."""
        try:
            await handler(**payload)
        except Exception as handler_fault:
            logger.error(
                f"Catastrophic failure within event handler for type '{event_type}': "
                f"{handler_fault}", exc_info=True
            )

    async def broadcast(self, event_type: str, **payload: Any) -> None:
        """Forwards an event across the entire system bus, including potential Redis inter-node channels."""
        # Implementation hook for cross-node Redis Pub/Sub if needed for distributed cluster sync
        await self.publish(event_type, **payload)
        logger.info(f"Broadcasted domain event: '{event_type}' with payload keys: {list(payload.keys())}")
