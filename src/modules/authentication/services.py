# services.py
"""Production-grade Authentication Service.

Encapsulates all business logic for user lifecycle management, session handling, 
and identity verification. This service orchestrates interactions between the 
database repositories, event bus, and caching layer to ensure atomic and 
consistent user operations across the platform.
"""

import logging
from typing import Final, Optional
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
        session_manager: Any
    ) -> None:
        self._user_repo: Final = user_repo
        self._wallet_service: Final = wallet_service
        self._event_bus: Final = event_bus
        self._session_manager: Final = session_manager

    async def is_registered(self, telegram_id: int) -> bool:
        """Verifies if the telegram user exists in the system."""
        return await self._user_repo.exists(telegram_id=telegram_id)

    async def register_user(
        self, telegram_id: int, phone_number: str, username: Optional[str] = None
    ) -> dict:
        """
        Orchestrates the atomic registration flow: 
        User record creation -> Wallet initialization -> Referral profile setup -> Event trigger.
        """
        logger.info(f"Initiating registration flow for Telegram ID: {telegram_id}")

        if await self.is_registered(telegram_id):
            raise ValueError("User already registered.")

        # Atomic Registration
        async with self._user_repo.transaction():
            user_data = UserRegistrationDTO(
                telegram_id=telegram_id,
                phone_number=phone_number,
                username=username,
                referral_code=self._generate_unique_code()
            )
            
            user = await self._user_repo.create(user_data)
            await self._wallet_service.create_wallet(user.id)
            
            # Publish registration event for downstream modules (notifications, analytics)
            await self._event_bus.publish("user.registered", {"user_id": user.id})

        logger.info(f"Successfully registered user {user.id}")
        return {"user_id": user.id, "status": "active"}

    async def logout(self, telegram_id: int) -> None:
        """Invalidates all active sessions for the given user."""
        await self._session_manager.revoke_all(telegram_id)
        await self._event_bus.publish("user.logged_out", {"telegram_id": telegram_id})
        logger.info(f"User {telegram_id} logged out.")

    def _generate_unique_code(self) -> str:
        """Generates a secure, unique referral identifier."""
        return CryptoCipher.generate_token(length=8).upper()
