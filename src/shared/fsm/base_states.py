# base_states.py
"""Centralized Finite State Machine Group Definitions.

Defines the authoritative state machine blueprints governing user-bot interaction 
workflows. Provides structured, strongly-typed StateGroups for authentication, 
fiscal operations, and administrative governance, ensuring consistent state 
transition logic across all feature modules.
"""

from aiogram.fsm.state import State, StatesGroup
from typing import Final


class RegistrationStates(StatesGroup):
    """Workflow states for new user onboarding and identity verification."""
    INPUT_FULL_NAME: Final[State] = State()
    INPUT_PHONE_NUMBER: Final[State] = State()
    INPUT_EMAIL: Final[State] = State()
    CONFIRM_REGISTRATION: Final[State] = State()


class InvestmentStates(StatesGroup):
    """Workflow states for capital deployment and investment lifecycle management."""
    SELECT_PLAN: Final[State] = State()
    INPUT_AMOUNT: Final[State] = State()
    CONFIRM_PURCHASE: Final[State] = State()
    PROCESSING_PAYMENT: Final[State] = State()


class WalletStates(StatesGroup):
    """Workflow states for liquidity management, deposits, and withdrawals."""
    INPUT_DEPOSIT_AMOUNT: Final[State] = State()
    INPUT_WITHDRAWAL_AMOUNT: Final[State] = State()
    CONFIRM_WITHDRAWAL: Final[State] = State()
    INPUT_WALLET_ADDRESS: Final[State] = State()


class AdminStates(StatesGroup):
    """Workflow states for back-office administrative governance and control."""
    MANAGE_USERS: Final[State] = State()
    MANAGE_FINANCE: Final[State] = State()
    BROADCAST_MESSAGE: Final[State] = State()
    CONFIRM_SYSTEM_ACTION: Final[State] = State()


class SupportStates(StatesGroup):
    """Workflow states for user-facing support ticketing and resolution."""
    INPUT_TICKET_SUBJECT: Final[State] = State()
    INPUT_TICKET_MESSAGE: Final[State] = State()
    REVIEW_TICKET: Final[State] = State()


class ProfileStates(StatesGroup):
    """Workflow states for account customization and user preference settings."""
    EDIT_DISPLAY_NAME: Final[State] = State()
    CHANGE_PASSWORD: Final[State] = State()
    UPDATE_REFERRAL_CODE: Final[State] = State()
