# __init__.py
"""Shared Finite State Machine Subsystem Registry.

Aggregates and exposes the public FSM interfaces used to manage user interaction 
lifecycles, transactional context flows, and multi-step registration processes. 
Provides decoupled, thread-safe access to persistent state storage abstractions 
and centralized state group definitions.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly export public FSM components
from src.shared.fsm.storage import RedisFSMStorage
from src.shared.fsm.base_states import InvestmentStates, AdminStates, RegistrationStates

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "RedisFSMStorage",
    "InvestmentStates",
    "AdminStates",
    "RegistrationStates",
]
