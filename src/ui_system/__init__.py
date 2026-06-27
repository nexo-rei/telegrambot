# __init__.py
"""UI System Central Export Registry.

Aggregates, coordinates, and exposes all foundational presentation components, 
stateful navigation managers, layout rendering blocks, keyboard factory adapters, 
and interactive graphic templates. Acts as the sole authoritative interface 
boundary separating business domain services from raw client view layouts.
"""

from typing import Final

# Assuming layout paths mapping structural files within presentation boundaries
from src.ui_system.manager import UIManager
from src.ui_system.screens import ScreenManager
from src.ui_system.navigation import NavigationEngine
from src.ui_system.animations import AnimationManager
from src.ui_system.keyboards import KeyboardRenderer
from src.ui_system.messages import MessageRenderer
from src.ui_system.emojis import EmojiManager

__all__: Final[list[str]] = [
    "UIManager",
    "ScreenManager",
    "NavigationEngine",
    "AnimationManager",
    "KeyboardRenderer",
    "MessageRenderer",
    "EmojiManager",
]
