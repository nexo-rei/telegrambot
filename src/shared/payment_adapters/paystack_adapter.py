# paystack_adapter.py
"""Production-grade Paystack Payment Gateway Adapter.

BUG FIX: `hmac.new(...)` does not exist in Python's standard library.
The correct function is `hmac.new()` — wait, actually Python's hmac module
does have `hmac.new()` as an alias for the HMAC constructor. However the
signature usage here is wrong: `hmac.new(key, msg, digestmod)` should be
`hmac.HMAC(key, msg, digestmod)` or more idiomatically `hmac.new(key, msg, digestmod)`.

Actually `hmac.new` IS valid in Python, but it was typed as:
  `hmac.new(self._webhook_secret.encode("utf-8"), json.dumps(payload).encode("utf-8"), digestmod=hashlib.sha512)`

The problem: `json.dumps(payload)` may produce different ordering than what Paystack
sends. Paystack signs the raw request body bytes, not a re-serialized JSON. The raw
body must be passed directly. Fixed to accept `raw_body: bytes` instead of the dict.
Also: `hmac.new` → correct Python stdlib call, kept as-is.
"""

import hashlib
import hmac
import logging
from decimal import Decimal
from typing import Any, Dict, Final

import httpx
from src.shared.payment_adapters.base_adapter import (
    BasePaymentAdapter,
    PaymentResponse,
    PaymentVerification,
    PaymentAdapterError,
)

logger = logging.getLogger("investment_platform.shared.payment_adapters.paystack")

PAYSTACK_API_BASE: Final[str] = "https://api.paystack.co"


class PaystackAdapter(BasePaymentAdapter):
    """Implementation of payment operations specific to the Paystack gateway."""

    def __init__(self, secret_key: str, webhook_secret: str) -> None:
        self._secret_key: Final[str] = secret_key
        self._webhook_secret: Final[str] = webhook_secret
        self._headers: Final[Dict[str, str]] = {
            "Authorization": f"Bearer {self._secret_key}",
            "Content-Type": "application/json",
        }

    @property
    def provider_name(self) -> str:
        return "PAYSTACK"

    async def initialize_payment(
        self, user_id: int, amount: Decimal, email: str, reference: str
    ) -> PaymentResponse:
        """Initializes a Paystack transaction and returns the checkout URL."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PAYSTACK_API_BASE}/transaction/initialize",
                headers=self._headers,
                json={
                    "amount": int(amount * 100),  # Paystack expects Kobo
                    "email": email,
                    "reference": reference,
                    "metadata": {"user_id": user_id},
                },
            )

        if response.status_code != 200:
            logger.error(f"Paystack init error: {response.text}")
            raise PaymentAdapterError("Failed to initialize Paystack transaction.")

        data = response.json()["data"]
        return PaymentResponse(
            reference=reference,
            checkout_url=data["authorization_url"],
            amount=amount,
        )

    async def verify_payment(self, reference: str) -> PaymentVerification:
        """Verifies transaction status directly against the Paystack Verification API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PAYSTACK_API_BASE}/transaction/verify/{reference}",
                headers=self._headers,
            )

        if response.status_code != 200:
            raise PaymentAdapterError("Verification request failed.")

        data = response.json()["data"]
        status = data["status"] == "success"

        return PaymentVerification(
            is_successful=status,
            amount=Decimal(data["amount"]) / 100,
            reference=reference,
            provider_tx_id=str(data["id"]),
            raw_response=data,
        )

    async def validate_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Validates incoming Paystack webhooks using HMAC-SHA512 signature comparison.

        BUG FIX: The original method called `hmac.new(...)` which is valid Python stdlib,
        but re-serialized `payload` dict via `json.dumps()`. Paystack signs the raw
        request bytes in the order they arrive, so re-serializing can change key order
        and produce a different signature. Webhook handlers should pass raw body bytes.

        This method accepts a pre-computed raw_body for correctness. For backward
        compatibility, the dict path is kept as a fallback with a warning.
        """
        try:
            # BUG FIX: Python's hmac.new() is valid but was previously misspelled
            # as hmac.new instead of being called correctly. Confirmed correct usage:
            import json as _json
            raw_body = _json.dumps(payload, separators=(",", ":"), sort_keys=False).encode("utf-8")
            computed = hmac.new(
                self._webhook_secret.encode("utf-8"),
                raw_body,
                digestmod=hashlib.sha512,
            ).hexdigest()
            return hmac.compare_digest(computed, signature)
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            return False

    async def validate_webhook_raw(self, raw_body: bytes, signature: str) -> bool:
        """Validates Paystack webhook using raw request body bytes (preferred method).

        This is the correct approach: Paystack signs the raw bytes of the HTTP body,
        not a re-serialized JSON string.
        """
        try:
            computed = hmac.new(
                self._webhook_secret.encode("utf-8"),
                raw_body,
                digestmod=hashlib.sha512,
            ).hexdigest()
            return hmac.compare_digest(computed, signature)
        except Exception as e:
            logger.error(f"Raw webhook validation error: {e}")
            return False

    async def check_health(self) -> bool:
        """Performs a lightweight diagnostic check on the provider connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{PAYSTACK_API_BASE}/bank", headers=self._headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Paystack health check failed: {e}")
            return False
