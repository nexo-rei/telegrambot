# states.py
"""Withdrawals Module FSM State Definitions.

Centralizes the Finite State Machine (FSM) state groups for all withdrawal-related 
workflows. Manages the lifecycle of a financial payout, from initial 
amount entry and bank account selection to final confirmation and automated 
payout reconciliation via external payment gateways.
"""

from aiogram.fsm.state import State, StatesGroup


class WithdrawalStates(StatesGroup):
    """Encapsulates all possible states within the withdrawal transaction lifecycle."""

    # Primary Navigation
    IDLE = State()
    LOADING_WITHDRAWAL = State()
    VIEWING_WITHDRAWAL_HOME = State()

    # Amount & Account Selection
    WAITING_FOR_WITHDRAWAL_AMOUNT = State()
    WAITING_FOR_BANK_SELECTION = State()
    WAITING_FOR_NEW_BANK_DETAILS = State()

    # Confirmation & Processing
    WAITING_FOR_CONFIRMATION = State()
    INITIALIZING_PAYOUT = State()
    WAITING_FOR_PAYOUT_COMPLETION = State()
    VERIFYING_WITHDRAWAL = State()

    # History & Detailed Views
    VIEWING_PENDING_WITHDRAWALS = State()
    VIEWING_WITHDRAWAL_HISTORY = State()
    VIEWING_WITHDRAWAL_DETAILS = State()

    # Terminal & Administrative States
    WAITING_FOR_CANCELLATION_CONFIRMATION = State()
    PROCESSING_WITHDRAWAL_OPERATION = State()
    
    # Terminal Statuses
    WITHDRAWAL_COMPLETED = State()
    WITHDRAWAL_FAILED = State()
    WITHDRAWAL_CANCELLED = State()
    WITHDRAWAL_REVERSED = State()
