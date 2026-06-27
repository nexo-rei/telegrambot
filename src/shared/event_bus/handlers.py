# handlers.py
"""Domain Event Handler Orchestration Framework.

Provides the foundational abstraction layer for processing asynchronous domain events.
Defines lifecycle hooks, filtering mechanisms, and middleware pipelines to ensure 
consistent, observable, and resilient event execution across the platform's core services.
"""

import abc
import logging
from dataclasses import dataclass, field
from typing import Any, Final, Optional, Protocol

logger = logging.getLogger("investment_platform.shared.event_bus.handlers")


@dataclass(frozen=True)
class HandlerContext:
    """Encapsulates execution context and metadata for domain event processing."""
    event_type: str
    payload: dict[str, Any]
    correlation_id: str
    timestamp: float


class EventHandler(abc.ABC):
    """Abstract base class governing the lifecycle of a domain event handler."""

    @abc.abstractmethod
    async def handle(self, context: HandlerContext) -> None:
        """Core logic implementation for the domain event handler."""
        pass

    async def before_handle(self, context: HandlerContext) -> None:
        """Lifecycle hook: Pre-processing execution block."""
        pass

    async def after_handle(self, context: HandlerContext) -> None:
        """Lifecycle hook: Post-processing execution block."""
        pass

    async def on_failure(self, context: HandlerContext, error: Exception) -> None:
        """Lifecycle hook: Failure isolation and recovery management."""
        logger.error(
            f"Handler failure encountered in {self.__class__.__name__} "
            f"for event {context.event_type}: {error}"
        )


class EventFilter(Protocol):
    """Protocol for defining event filtering predicates."""
    def __call__(self, context: HandlerContext) -> bool: ...


@dataclass
class EventHandlerRegistry:
    """Manages the lifecycle, priority, and routing of registered event handlers."""
    
    _handlers: dict[str, list[EventHandler]] = field(default_factory=dict)
    _filters: dict[str, list[EventFilter]] = field(default_factory=dict)

    def register(self, event_type: str, handler: EventHandler) -> None:
        """Registers a handler instance for a specific domain event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler {handler.__class__.__name__} for event '{event_type}'")

    def add_filter(self, event_type: str, filter_func: EventFilter) -> None:
        """Adds a predicate filter to refine event propagation."""
        if event_type not in self._filters:
            self._filters[event_type] = []
        self._filters[event_type].append(filter_func)

    def get_eligible_handlers(self, context: HandlerContext) -> list[EventHandler]:
        """Returns handlers that pass all registered filter predicates."""
        event_type = context.event_type
        
        # Validate all filters
        for filter_func in self._filters.get(event_type, []):
            if not filter_func(context):
                return []
        
        return self._handlers.get(event_type, [])


class LoggingEventHandler(EventHandler):
    """Standardized handler for auditing event occurrences to system logs."""
    
    async def handle(self, context: HandlerContext) -> None:
        logger.info(
            f"Event Dispatch: [{context.event_type}] | "
            f"Correlation: {context.correlation_id} | "
            f"Payload: {context.payload}"
        )
