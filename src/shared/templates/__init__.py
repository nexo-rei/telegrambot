"""Shared Message Templating and UI Rendering Subsystem Registry.

Aggregates and exposes the public interfaces for managing centralized Telegram 
message templates. Provides a standardized mechanism for rendering high-fidelity 
UI text, Markdown formatting, and dynamic notification content, ensuring consistent 
brand voice and visual presentation across the entire platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public template management components
from src.shared.templates.message_templates import MessageTemplates, TemplateRenderer

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "MessageTemplates",
    "TemplateRenderer",
]
