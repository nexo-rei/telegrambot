"""
Custom exceptions for the Support Tickets module.
"""


class SupportTicketError(Exception):
    """Base exception raised for support ticket related failures."""

    def __init__(self, message: str = "Support ticket operation failed.") -> None:
        super().__init__(message)
