"""User Specific Database Repository.

Extends the generic base repository layer to implement highly optimized,
index-aware asynchronous queries for the User model. Handles analytical aggregates,
security telemetry updates, multi-layered referral lookups, and transactional account updates.
"""

from datetime import datetime, UTC, timedelta
import logging
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, update, exc
from sqlalchemy.engine import Result

from database.repositories.base_repo import BaseRepository
from database.models.user import User
from database.models.wallet import Wallet

logger = logging.getLogger("investment_platform.repositories.user")


class UserRepository(BaseRepository[User]):
    """Production-ready database abstraction layer for execution of User state updates."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the repository with an explicit User model binding."""
        super().__init__(User, session)

    # --- User Lookup Methods ---

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Retrieves a user utilizing their unique 64-bit unique Telegram index."""
        try:
            statement = select(User).where(User.telegram_id == telegram_id)
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed lookup for telegram_id {telegram_id}: {error}")
            raise error

    async def get_by_username(self, username: str) -> User | None:
        """Fetches a record matching a precise normalized Telegram username handle."""
        try:
            statement = select(User).where(User.username == username.lstrip("@"))
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed lookup for username {username}: {error}")
            raise error

    async def get_by_email(self, email: str) -> User | None:
        """Locates an unique participant record via their registered email address string."""
        try:
            statement = select(User).where(User.email == email.strip().lower())
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed lookup for email {email}: {error}")
            raise error

    async def get_by_phone(self, phone: str) -> User | None:
        """Locates an unique participant record via their international format MSISDN phone string."""
        try:
            statement = select(User).where(User.phone == phone.strip())
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed lookup for phone {phone}: {error}")
            raise error

    async def get_by_referral_code(self, referral_code: str) -> User | None:
        """Locates a referrer node leveraging their unique affiliate platform alpha-numeric string."""
        try:
            statement = select(User).where(User.referral_code == referral_code.strip())
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed lookup for referral_code {referral_code}: {error}")
            raise error

    # --- Governance & Authentication States Matrix ---

    async def create_user(self, payload: dict[str, Any]) -> User:
        """Registers a verified participant within the persistence layer engine.

        Automatically ensures explicit fields mapping and establishes an 
        associated blank Wallet model matrix inside a singular transaction unit.
        """
        try:
            user = User(**payload)
            self.session.add(user)
            await self.session.flush()

            wallet = Wallet(
                user_id=user.telegram_id,
                currency=payload.get("currency", "NGN")
            )
            self.session.add(wallet)
            await self.session.flush()
            
            return user
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed atomic user creation cycle: {error}")
            await self.session.rollback()
            raise error

    async def verify_user(self, telegram_id: int) -> bool:
        """Enforces structural validation updates elevating an profile status to verified."""
        return await self.update_by_id(telegram_id, {"is_verified": True})

    async def ban_user(self, telegram_id: int, status_reason: str = "BANNED") -> bool:
        """Applies a security lock down flag, denying platform access privileges."""
        return await self.update_by_id(telegram_id, {"is_banned": True, "account_status": status_reason})

    async def unban_user(self, telegram_id: int) -> bool:
        """Removes a security lock down flag, restoring structural platform access paths."""
        return await self.update_by_id(telegram_id, {"is_banned": False, "account_status": "ACTIVE"})

    async def activate_user(self, telegram_id: int) -> bool:
        """Sets the structural Boolean flag to bring an identity target state inline."""
        return await self.update_by_id(telegram_id, {"is_active": True})

    async def deactivate_user(self, telegram_id: int) -> bool:
        """Sets the structural Boolean flag to place an identity target state out of service."""
        return await self.update_by_id(telegram_id, {"is_active": False})

    # --- Telemetry Interactivity Trackers ---

    async def update_last_login(self, telegram_id: int, ip_address: str | None = None) -> bool:
        """Records chronological login metadata strings alongside regional geolocation footprint vectors."""
        payload = {"last_login": datetime.now(UTC)}
        if ip_address:
            payload["last_ip"] = ip_address
        return await self.update_by_id(telegram_id, payload)

    async def update_last_activity(self, telegram_id: int) -> bool:
        """Maintains dynamic session timing indices to gauge concurrent utilization profiles."""
        return await self.update_by_id(telegram_id, {"last_activity": datetime.now(UTC)})

    async def update_last_message(self, telegram_id: int, message_text: str) -> bool:
        """Saves incoming string payloads to provide analytical logging contexts on message reception."""
        return await self.update_by_id(telegram_id, {"last_message": message_text[:4000], "last_activity": datetime.now(UTC)})

    async def update_last_callback(self, telegram_id: int, callback_data: str) -> bool:
        """Saves incoming query elements to provide analytical logging contexts on callback reception."""
        return await self.update_by_id(telegram_id, {"last_callback": callback_data[:256], "last_activity": datetime.now(UTC)})

    # --- Multi-Tenant System Metrics & Structural Aggregates ---

    async def total_users(self) -> int:
        """Returns the total number of registration footprints inside the engine database."""
        return await self.count()

    async def active_users(self) -> int:
        """Returns the total number of non-banned and fully functional operational accounts."""
        return await self.count(is_active=True, is_banned=False)

    async def banned_users(self) -> int:
        """Returns the total count of profiles intercepted or flag-locked under suspension parameters."""
        return await self.count(is_banned=True)

    async def verified_users(self) -> int:
        """Returns the total count of records cleared through KYC or administrative validation checkpoints."""
        return await self.count(is_verified=True)

    async def admin_users(self) -> int:
        """Returns the total count of high-level privilege access governance profiles."""
        return await self.count(is_admin=True)

    async def moderator_users(self) -> int:
        """Returns the total count of intermediate level security tracking profiles."""
        return await self.count(is_moderator=True)

    # --- Affiliate Networking Matrix Operations ---

    async def increment_referral_count(self, telegram_id: int) -> bool:
        """Atomically steps up downline generation trackers on an active node handle."""
        try:
            statement = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(referral_count=User.referral_count + 1)
            )
            result = await self.session.execute(statement)
            return (result.rowcount or 0) > 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed atomic increment execution on referrer {telegram_id}: {error}")
            raise error

    async def update_referral_bonus(self, telegram_id: int, incremental_reward: Decimal) -> bool:
        """Adds to an affiliate balance while ensuring lifetime statistics increment synchronously."""
        try:
            statement = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    bonus_balance=User.bonus_balance + incremental_reward,
                    total_referral_bonus=User.total_referral_bonus + incremental_reward
                )
            )
            result = await self.session.execute(statement)
            return (result.rowcount or 0) > 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed performance increment on referral rewards tracker {telegram_id}: {error}")
            raise error

    async def get_referrals(self, telegram_id: int) -> Sequence[User]:
        """Exposes the immediate first-tier downstream array nodes tracking downline links."""
        try:
            statement = select(User).where(User.referred_by == telegram_id).order_by(desc(User.created_at))
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed downline tree selection for node {telegram_id}: {error}")
            raise error

    # --- Wallet Sub-Graph Linkages Mapping ---

    async def get_wallet(self, telegram_id: int) -> Wallet | None:
        """Executes targeted selections returning liquid balance records corresponding to a user identity."""
        try:
            statement = select(Wallet).where(Wallet.user_id == telegram_id)
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed sub-graph mapping retrieval for user wallet {telegram_id}: {error}")
            raise error

    async def update_wallet_balance(
        self, telegram_id: int, available_delta: Decimal, bonus_delta: Decimal = Decimal("0.00")
    ) -> bool:
        """Modifies core cash allocations using multi-parameter tracking elements."""
        try:
            statement = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(
                    wallet_balance=User.wallet_balance + available_delta,
                    bonus_balance=User.bonus_balance + bonus_delta
                )
            )
            result = await self.session.execute(statement)
            return (result.rowcount or 0) > 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed transaction balance assignment on user table index {telegram_id}: {error}")
            raise error

    # --- Forensic Matrix Query Searching Functions ---

    async def search_users(self, Search_term: str) -> Sequence[User]:
        """Evaluates complex partial sub-string constraints matching text data records."""
        try:
            sanitized = f"%{search_term.strip()}%"
            statement = select(User).where(
                or_(
                    User.username.ilike(sanitized),
                    User.full_name.ilike(sanitized),
                    User.email.ilike(sanitized),
                    User.phone.ilike(sanitized)
                )
            ).order_by(desc(User.created_at))
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed complex string matrix parsing search on context: {search_term}: {error}")
            raise error

    async def search_by_name(self, full_name_term: str) -> Sequence[User]:
        """Isolates search constraints exclusively to real-name identity tags."""
        try:
            statement = select(User).where(User.full_name.ilike(f"%{full_name_term.strip()}%"))
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed pattern match query on name target {full_name_term}: {error}")
            raise error

    async def search_by_username(self, username_term: str) -> Sequence[User]:
        """Isolates search constraints exclusively to Telegram structural aliases."""
        try:
            statement = select(User).where(User.username.ilike(f"%{username_term.strip().lstrip('@')}%"))
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed pattern match query on username handle target {username_term}: {error}")
            raise error

    # --- Administrative Telemetry Functions ---

    async def latest_users(self, limit_count: int = 50) -> Sequence[User]:
        """Pulls a fixed window collection tracking the most recently registered profiles."""
        try:
            statement = select(User).order_by(desc(User.created_at)).limit(limit_count)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed chronological profile pull limit context: {limit_count}: {error}")
            raise error

    async def users_registered_today(self) -> int:
        """Calculates total onboarding conversion volume for the current calendar date."""
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            statement = select(func.count()).select_from(User).where(User.created_at >= today_start)
            result = await self.session.execute(statement)
            return int(result.scalar() or 0)
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed daily timeline accumulation lookup: {error}")
            raise error

    async def users_registered_this_week(self) -> int:
        """Calculates total onboarding conversion volume tracking back across 7 calendar days."""
        week_start = datetime.now(UTC) - timedelta(days=7)
        try:
            statement = select(func.count()).select_from(User).where(User.created_at >= week_start)
            result = await self.session.execute(statement)
            return int(result.scalar() or 0)
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed weekly timeline accumulation lookup: {error}")
            raise error

    async def users_registered_this_month(self) -> int:
        """Calculates total onboarding conversion volume tracking back across 30 calendar days."""
        month_start = datetime.now(UTC) - timedelta(days=30)
        try:
            statement = select(func.count()).select_from(User).where(User.created_at >= month_start)
            result = await self.session.execute(statement)
            return int(result.scalar() or 0)
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed monthly timeline accumulation lookup: {error}")
            raise error
