# states.py
"""Dashboard Module FSM State Definitions.

Centralizes the Finite State Machine (FSM) state groups for all dashboard 
interactions and navigation flows. Defines structured states to manage 
the user's context within the dashboard, ensuring seamless transitions 
between financial summaries, account settings, and investment views.
"""

from aiogram.fsm.state import State, StatesGroup


class DashboardStates(StatesGroup):
    """Encapsulates all possible states within the dashboard navigation flow."""

    # Main Dashboard Views
    IDLE = State()
    LOADING_DASHBOARD = State()
    MAIN_VIEW = State()
    REFRESHING_DASHBOARD = State()

    # Sectional Views
    VIEWING_WALLET_SUMMARY = State()
    VIEWING_INVESTMENT_SUMMARY = State()
    VIEWING_EARNINGS_SUMMARY = State()
    VIEWING_REFERRAL_SUMMARY = State()
    VIEWING_STATISTICS = State()

    # Communication & History
    VIEWING_NOTIFICATIONS = State()
    VIEWING_ANNOUNCEMENTS = State()
    VIEWING_RECENT_TRANSACTIONS = State()

    # Settings & User Management
    VIEWING_PROFILE = State()
    VIEWING_SETTINGS = State()
    VIEWING_QUICK_ACTIONS = State()
