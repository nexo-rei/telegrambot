# __init__.py
"""Admin Panel Module Registry.

Aggregates and exposes the public interfaces for the platform's administrative 
control and management subsystem. This module provides authorized operators 
with tools for user oversight, financial auditing, system configuration, 
and platform maintenance within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public admin panel components
from src.modules.admin_panel.handlers import AdminPanelHandlers
from src.modules.admin_panel.services import AdminPanelService
from src.modules.admin_panel.keyboards import AdminPanelKeyboards

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AdminPanelHandlers",
    "AdminPanelService",
    "AdminPanelKeyboards",
]
