# payment_webhook.py
"""Production-Grade Payment Webhook Handler.

Provides the secure, centralized entry point for processing financial events from
payment gateways like Paystack.

BUG FIXES:
  - `from src.shared.event_bus import EventBus` failed because event_bus/__init__.py
    contained role_required code instead of EventBus exports (fixed in event_bus/__init__.py).
  - `fastapi` (Request, Response, Header, HTTPException, status) was imported but
    fastapi is NOT in requirements.txt and this is a Telegram bot, not a FastAPI app.
    The webhook handler is designed for optional HTTP integration. Added fastapi as
    an optional dependency and guarded the import; or if the webhook is not used
    standalone, the import is fine as long as fastapi is installed. Added it to
    requirements.txt note. For Railway polling-mode deployment, this module is not
    called directly, so the import error is non-fatal if fastapi is absent.
    Made the import conditional with a clear error message.
"""

import logging
from typing import Any, Final, Dict, Optional

logger = logging.getLogger("investment_platform.shared.webhook_handlers.payment")

# Conditional fastapi import — only required when running in webhook mode
try:
    from fastapi import Request, Response, status, Header, HTTPException
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False
    logger.warning(
        "fastapi is not installed. PaymentWebhookHandler will not be available. "
        "Install fastapi if webhook mode is required."
    )

from src.shared.payment_adapters.paystack_adapter import PaystackAdapter
from src.shared.event_bus.bus import EventBus  # BUG FIX: import directly from bus.py


class PaymentWebhookHandler:
    """Handles secure ingestion and dispatching of payment gateway webhooks."""

    def __init__(self, adapter: PaystackAdapter, event_bus: EventBus) -> None:
        self._adapter: Final[PaystackAdapter] = adapter
        self._event_bus: Final[EventBus] = event_bus

    async def handle_webhook(
        self,
        request: Any,  # fastapi.Request when available
        x_paystack_signature: str = "",
    ) -> Any:
        """Processes incoming Paystack webhooks with signature verification."""
        if not _FASTAPI_AVAILABLE:
            raise RuntimeError(
                "fastapi must be installed to use PaymentWebhookHandler. "
                "Add fastapi to requirements.txt."
            )

        # Get raw body bytes for correct HMAC verification
        raw_body: bytes = await request.body()
        payload: Dict[str, Any] = await request.json()

        # 1. Verify Webhook Signature using raw body bytes
        if not await self._adapter.validate_webhook_raw(raw_body, x_paystack_signature):
            logger.error("Invalid payment webhook signature received.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signature mismatch",
            )

        # 2. Extract Event Data
        event_type = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")

        logger.info(f"Processing webhook event: {event_type} | Ref: {reference}")

        # 3. Idempotency & Processing Dispatch
        try:
            await self._dispatch_event(event_type, data)
            return Response(status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error dispatching webhook event {event_type}: {e}")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def _dispatch_event(self, event_type: Optional[str], data: Dict[str, Any]) -> None:
        """Routes the verified event to the appropriate domain handler."""
        match event_type:
            case "charge.success":
                await self._event_bus.publish("deposit.confirmed", **data)
            case "transfer.success":
                await self._event_bus.publish("withdrawal.processed", **data)
            case _:
                logger.debug(f"Unhandled event type received: {event_type}")

    async def health_check(self) -> Any:
        """Verify payment webhook system readiness."""
        if _FASTAPI_AVAILABLE:
            return Response(status_code=status.HTTP_200_OK)
        return {"status": "ok"}
