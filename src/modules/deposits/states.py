# states.py
"""Deposits Module FSM State Definitions.

Centralizes the Finite State Machine (FSM) state groups for all deposit-related 
workflows. Manages the lifecycle of a financial transaction, from initial 
amount entry and gateway selection to payment verification and terminal 
status processing (completion, failure, or cancellation).
"""

from aiogram.fsm.state import State, StatesGroup


class DepositStates(StatesGroup):
    """Encapsulates all possible states within the deposit transaction lifecycle."""

    # Primary Navigation
    IDLE = State()
    LOADING_DEPOSIT = State()
    VIEWING_DEPOSIT_HOME = State()

    # Amount & Method Selection
    WAITING_FOR_DEPOSIT_AMOUNT = State()
    WAITING_FOR_PAYMENT_METHOD = State()

    # Payment Lifecycle
    INITIALIZING_PAYMENT = State()
    WAITING_FOR_PAYMENT_VERIFICATION = State()
    VERIFYING_PAYMENT = State()

    # History & Detailed Views
    VIEWING_PENDING_DEPOSITS = State()
    VIEWING_DEPOSIT_HISTORY = State()
    VIEWING_DEPOSIT_DETAILS = State()

    # Terminal & Administrative States
    WAITING_FOR_CANCELLATION_CONFIRMATION = State()
    PROCESSING_DEPOSIT_OPERATION = State()
    
    # Terminal Statuses
    DEPOSIT_COMPLETED = State()
    DEPOSIT_FAILED = State()
    DEPOSIT_CANCELLED = State()
    DEPOSIT_EXPIRED = State()
