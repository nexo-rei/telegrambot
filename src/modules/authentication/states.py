# states.py
"""Authentication Module FSM State Definitions.

Centralizes the Finite State Machine (FSM) state groups for all authentication 
and onboarding workflows. Defines discrete, production-ready states to manage 
user input sequences, ensuring robust session handling and input validation 
during registration, login, and recovery processes.
"""

from aiogram.fsm.state import State, StatesGroup


class AuthenticationStates(StatesGroup):
    """Encapsulates all possible states within the authentication flow."""

    # Onboarding & Terms
    WAITING_FOR_START = State()
    ACCEPT_TERMS = State()
    ACCEPT_PRIVACY = State()

    # Registration Flow
    WAITING_FOR_REFERRAL_CODE = State()
    REGISTRATION_PENDING = State()
    REGISTRATION_COMPLETED = State()

    # Login & Authentication
    WAITING_FOR_AUTHENTICATION = State()
    WAITING_FOR_SESSION_VALIDATION = State()
    LOGIN_COMPLETED = State()

    # Recovery Flow
    WAITING_FOR_RECOVERY_REQUEST = State()
    WAITING_FOR_RECOVERY_CONFIRMATION = State()
    RECOVERY_COMPLETED = State()

    # Utility States
    LOGOUT_CONFIRMATION = State()
