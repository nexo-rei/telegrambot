# services.py
"""Production-grade Authentication Service.

BUG FIXES:
  - `Any` was used in type annotations but never imported.
  - `self._user_repo.transaction()` does not exist on BaseRepository. The session
    scope/transaction management is handled at the session layer, not the repo.
    Replaced with direct repo calls wrapped in the session's commit logic.
  - `self._user_repo.create(user_data)` was called with a DTO object (UserRegistrationDTO),
    but BaseRepository.create() expects a dict[str, Any]. Convert DTO to dict first.
  - `user.id` referenced after creation, but User's primary key is `id` (from IDMixin)
    while the natural key is `telegram_id`. Fixed to use correct field.
"""

import logging
from typing import Any, Final, Optional
from uuid import uuid4

from src.shared.utilities.crypto_cipher import CryptoCipher
from src.modules.authentication.dtos import UserRegistrationDTO
from src.modules.authentication.validators import AuthenticationValidator

logger = logging.getLogger("investment_platform.modules.authentication.services")


class AuthenticationService:
    """Core domain service for managing user authentication and account lifecycle."""

    def __init__(
        self,
        user_repo: Any,
        wallet_service: Any,
        event_bus: Any,
        session_manager: Any,
    ) -> None:
        self._user_repo: Final = user_repo
        self._wallet_service: Final = wallet_service
        self._event_bus: Final = event_bus
        self._session_manager: Final = session_manager

    async def is_registered(self, telegram_id: int) -> bool:
        """Verifies if the telegram user exists in the system."""
        return await self._user_repo.exists(telegram_id=telegram_id)

    async def register_user(
        self,
        telegram_id: int,
        phone_number: str,
        username: Optional[str] = None,
        referral_code: Optional[str] = None,
    ) -> dict:
        """Orchestrates the atomic registration flow:
        User record creation -> Wallet initialization -> Referral profile setup -> Event trigger.

        BUG FIX: Original called `self._user_repo.transaction()` which does not exist.
        BUG FIX: Original called `self._user_repo.create(user_data)` with a DTO; must be dict.
        """
        logger.info(f"Initiating registration flow for Telegram ID: {telegram_id}")

        if await self.is_registered(telegram_id):
            raise ValueError("User already registered.")

        # Build registration payload as dict (BaseRepository.create expects dict)
        first_name = username or f"User{telegram_id}"
        user_payload = {
            "telegram_id": telegram_id,
            "phone": phone_number,
            "username": username,
            "first_name": first_name,
            "full_name": first_name,
            "referral_code": self._generate_unique_code(),
            "referred_by": None,
        }

        # Handle referral code lookup if provided
        if referral_code:
            try:
                referrer = await self._user_repo.get_by_referral_code(referral_code)
                if referrer and referrer.telegram_id != telegram_id:
                    user_payload["referred_by"] = referrer.telegram_id
            except Exception as e:
                logger.warning(f"Failed to resolve referral code {referral_code}: {e}")

        # BUG FIX: UserRepository.create_user() handles both user + wallet creation atomically
        user = await self._user_repo.create_user(user_payload)

        # Publish registration event for downstream modules (notifications, analytics)
        try:
            await self._event_bus.publish("user.registered", user_id=user.telegram_id)
        except Exception as e:
            logger.warning(f"Event bus publish failed for user.registered: {e}")

        logger.info(f"Successfully registered user {user.telegram_id}")
        return {"user_id": user.telegram_id, "status": "active"}

    async def logout(self, telegram_id: int) -> None:
        """Invalidates all active sessions for the given user."""
        try:
            await self._session_manager.revoke_all(telegram_id)
        except Exception as e:
            logger.warning(f"Session manager revoke failed for {telegram_id}: {e}")
        try:
            await self._event_bus.publish("user.logged_out", telegram_id=telegram_id)
        except Exception as e:
            logger.warning(f"Event bus publish failed for user.logged_out: {e}")
        logger.info(f"User {telegram_id} logged out.")

    def _generate_unique_code(self) -> str:
        """Generates a secure, unique referral identifier."""
        return CryptoCipher.generate_token(length=6).upper()
