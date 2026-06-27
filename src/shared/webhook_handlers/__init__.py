# __init__.py
"""Shared Webhook Handler Subsystem Registry.

Aggregates and exposes the public interfaces for processing incoming HTTP 
webhooks from external providers, including Telegram and payment gateways. 
Ensures a secure, centralized entry point for asynchronous event ingestion, 
validation, and routing to core business services.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public webhook management components
from src.shared.webhook_handlers.telegram_webhook import TelegramWebhookHandler
from src.shared.webhook_handlers.payment_webhook import PaymentWebhookHandler

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "TelegramWebhookHandler",
    "PaymentWebhookHandler",
]
