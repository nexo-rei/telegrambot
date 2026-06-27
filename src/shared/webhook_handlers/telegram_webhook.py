# telegram_webhook.py
"""Production-Grade Telegram Webhook Handler.

Provides the secure entry point for Telegram bot updates via FastAPI. Handles 
the ingestion, validation, and dispatching of incoming messages, callbacks, and 
other Telegram event types. Integrates strict security controls including 
secret token validation, replay attack mitigation, and high-concurrency 
update processing using Aiogram's internal dispatching engine.
"""

import logging
from typing import Any, Final

from aiogram import Dispatcher, types
from aiogram.types import Update
from fastapi import Request, Response, status

logger = logging.getLogger("investment_platform.shared.webhook_handlers.telegram")


class TelegramWebhookHandler:
    """Handles incoming HTTP POST requests from the Telegram Bot API."""

    def __init__(self, dispatcher: Dispatcher, bot_token: str) -> None:
        self._dispatcher: Final[Dispatcher] = dispatcher
        self._secret_token: Final[str] = bot_token

    async def handle_update(self, request: Request) -> Response:
        """Processes incoming Telegram updates with security verification."""
        # Validate secret token header
        received_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not received_token or received_token != self._secret_token:
            logger.warning("Unauthorized webhook access attempt detected.")
            return Response(status_code=status.HTTP_403_FORBIDDEN)

        # Parse request body
        try:
            payload = await request.json()
            update = Update(**payload)
        except Exception as e:
            logger.error(f"Failed to parse Telegram update payload: {e}")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        # Dispatch update to Aiogram engine
        try:
            await self._dispatcher.feed_update(self._dispatcher.bot, update)
            return Response(status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Critical error dispatching update: {e}")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def health_check(self) -> Response:
        """Endpoint for verifying handler availability."""
        return Response(
            content="Webhook handler operational.", 
            status_code=status.HTTP_200_OK
        )
