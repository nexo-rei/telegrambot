# __init__.py
"""Asynchronous Domain Event Bus Package Registry.

BUG FIX: The original __init__.py contained the entire `role_required` decorator
implementation instead of event bus exports. This means:
  1. `from src.shared.event_bus import EventBus` would fail (EventBus not exported)
  2. The role_required decorator was unreachable from its natural home in decorators/
  3. payment_webhook.py: `from src.shared.event_bus import EventBus` would NameError

Fixed by making this file properly export EventBus from bus.py.
The role_required decorator belongs in src/shared/decorators/role_required.py (already there).
"""

from typing import Final

__version__: Final[str] = "2.0.0"

from src.shared.event_bus.bus import EventBus
from src.shared.event_bus.handlers import EventHandler, EventHandlerRegistry, HandlerContext

__all__: Final[list[str]] = [
    "__version__",
    "EventBus",
    "EventHandler",
    "EventHandlerRegistry",
    "HandlerContext",
]
