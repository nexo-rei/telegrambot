# states.py
"""Wallet Module FSM State Definitions.

Centralizes the Finite State Machine (FSM) state groups for all wallet-related 
interactions. Defines granular states for financial workflows, ensuring robust 
context management during deposits, withdrawals, and transaction history 
browsing within the platform.
"""

from aiogram.fsm.state import State, StatesGroup


class WalletStates(StatesGroup):
    """Encapsulates all possible states within the wallet navigation and operation flows."""

    # Primary Views
    IDLE = State()
    LOADING_WALLET = State()
    VIEWING_WALLET = State()
    REFRESHING_WALLET = State()

    # Financial Reporting
    VIEWING_BALANCE = State()
    VIEWING_STATISTICS = State()
    VIEWING_TRANSACTIONS = State()
    VIEWING_FINANCIAL_SUMMARY = State()

    # Deposit Workflow
    WAITING_FOR_DEPOSIT_AMOUNT = State()
    WAITING_FOR_DEPOSIT_CONFIRMATION = State()

    # Withdrawal Workflow
    WAITING_FOR_WITHDRAWAL_AMOUNT = State()
    WAITING_FOR_WITHDRAWAL_ADDRESS = State()
    WAITING_FOR_WITHDRAWAL_CONFIRMATION = State()

    # Processing & Utility
    PROCESSING_WALLET_OPERATION = State()
    SYNCHRONIZING_BALANCES = State()
