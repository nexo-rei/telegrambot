# payment_gateways.py
"""Payment Gateways Configuration Engine.

Defines, enforces, and locks down precise transactional boundaries, API endpoint
topologies, routing links, and error-retry behaviors specifically optimized for
the Nigerian financial ecosystem via Paystack (and inactive Flutterwave paths).
"""

from typing import Any, Dict
from config.base import settings


class PaystackConfig:
    """Explicit production configurations for the Paystack payment subsystem.

    Establishes operational constraints, verification signatures, and processing
    thresholds matching standard banking hours and liquidity flows in Nigeria.
    """

    # API Endpoint Mappings
    BASE_URL: str = "https://api.paystack.co"
    
    # Cryptographic Authentication Signatures
    SECRET_KEY: str = settings.payment.SECRET_KEY
    PUBLIC_KEY: str = settings.payment.PUBLIC_KEY
    WEBHOOK_SECRET: str = settings.payment.WEBHOOK_SECRET

    # Fixed Regional Asset Definition
    CURRENCY: str = "NGN"
    CURRENCY_SYMBOL: str = "₦"

    # Transaction Velocity Boundaries (Stated in Minor Units: Kobo -> ₦1.00 = 100 Kobo)
    # ₦100.00 Minimum limit enforced to mitigate card testing fraud
    MIN_TRANSACTION_AMOUNT_KOBO: int = 10_000 
    # ₦10,000,000.00 Maximum single-transaction settlement ceiling limit
    MAX_TRANSACTION_AMOUNT_KOBO: int = 1_000_000_000 

    # Traceability Isolation Keys
    TRANSACTION_PREFIX: str = "VEL-NGN-TX-"

    # HTTP Network Lifecycle Rules
    REQUEST_TIMEOUT_SECONDS: float = 15.0
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 2.0

    # Interaction Redirect Routes (Optional Fallback Targets for Webview Flows)
    CALLBACK_URL: str = f"{settings.bot.WEBHOOK_URL}/payment/callback" if settings.bot.WEBHOOK_URL else ""
    SUCCESS_URL: str = "https://t.me/" + settings.bot.USERNAME if settings.bot.USERNAME else ""
    CANCEL_URL: str = "https://t.me/" + settings.bot.USERNAME if settings.bot.USERNAME else ""

    # Integrity Controls Configuration
    ENFORCE_WEBHOOK_SIGNATURE_VERIFICATION: bool = True
    LOG_WEBHOOK_PAYLOADS: bool = True


class FlutterwaveConfig:
    """Future-Ready Blueprint Settings for Flutterwave Infrastructure.
    
    Deactivated by default for Phase 1 release containment.
    """
    IS_ENABLED: bool = False
    BASE_URL: str = "https://api.flutterwave.com/v3"
    CURRENCY: str = "NGN"
    TRANSACTION_PREFIX: str = "VEL-NGN-FLW-"


class PaymentGatewayConfig:
    """Root configuration aggregator overseeing the platform's transactional gateway state configurations."""

    # Active Provider Identification Flags
    PRIMARY_GATEWAY: str = "PAYSTACK"
    SUPPORTED_GATEWAYS: list[str] = ["PAYSTACK"]

    # Instantiated Configuration Interfaces
    paystack: PaystackConfig = PaystackConfig()
    flutterwave: FlutterwaveConfig = FlutterwaveConfig()

    @classmethod
    def get_operational_mode(cls) -> str:
        """Determines the production operational context based on the global runtime engine debug flags."""
        return "SANDBOX" if settings.flags.DEBUG else "PRODUCTION"

    @classmethod
    def get_gateway_metadata(cls) -> Dict[str, Any]:
        """Assembles telemetry structural states for payment pipeline checking hooks."""
        return {
            "active_gateway": cls.PRIMARY_GATEWAY,
            "operational_mode": cls.get_operational_mode(),
            "base_currency": PaystackConfig.CURRENCY,
            "min_amount_ngn": PaystackConfig.MIN_TRANSACTION_AMOUNT_KOBO / 100,
            "max_amount_ngn": PaystackConfig.MAX_TRANSACTION_AMOUNT_KOBO / 100,
            "paystack_webhook_configured": bool(PaystackConfig.WEBHOOK_SECRET)
        }
        
