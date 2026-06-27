# __init__.py
"""Authentication Module Registry.

Aggregates and exposes the public interfaces for the platform's authentication 
subsystem. This module manages user identity verification, session lifecycle, 
and secure access control entry points, ensuring all authentication processes 
adhere to strict enterprise security standards.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public authentication components
from src.modules.authentication.handlers import AuthenticationHandlers
from src.modules.authentication.services import AuthenticationService
from src.modules.authentication.keyboards import AuthenticationKeyboards
from src.modules.authentication.states import AuthenticationStates
from src.modules.authentication.dtos import AuthenticationDTOs
from src.modules.authentication.validators import AuthenticationValidator

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "AuthenticationHandlers",
    "AuthenticationService",
    "AuthenticationKeyboards",
    "AuthenticationStates",
    "AuthenticationDTOs",
    "AuthenticationValidator",
]
