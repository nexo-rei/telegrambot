"""Financial Domain Database Repository.

Authoritative high-throughput financial engine managing the platform's core ledger,
liquidity streams, wallet mutations, investment matrices, and referral bonus pipelines.
Enforces explicit row-level pessimism (SELECT FOR UPDATE) to eliminate transaction
race conditions, double-spend vectors, and floating-point calculation drift.
"""

from datetime import datetime, UTC
from decimal import Decimal
import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update, exc
from sqlalchemy.engine import Result

from database.repositories.base_repo import BaseRepository
from database.models.transaction import Transaction, TransactionType, TransactionStatus
from database.models.wallet import Wallet
from database.models.investment import Investment

logger = logging.getLogger("investment_platform.repositories.financial")


class FinancialRepository(BaseRepository[Transaction]):
    """Production-ready database abstraction layer for execution of ledger events."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the repository with an explicit Transaction model binding."""
        super().__init__(Transaction, session)

    # --- Deposits Subsystem ---

    async def create_deposit(self, user_id: int, wallet_id: int, amount: Decimal, fee: Decimal, external_ref: str, payment_ref: Optional[str] = None) -> Transaction:
        """Persists a pending primary entry inside the transaction ledger frame."""
        net_amount = amount - fee
        payload = {
            "user_id": user_id,
            "wallet_id": wallet_id,
            "type": TransactionType.DEPOSIT,
            "status": TransactionStatus.PENDING,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "external_reference": external_ref,
            "payment_reference": payment_ref,
            "description": f"Deposit initialization via Paystack: ₦{amount:,.2f}"
        }
        return await self.create(payload, auto_commit=False)

    async def get_deposit_by_reference(self, reference_str: str) -> Transaction | None:
        """Locates an active ledger payment entry leveraging unique identifier strings."""
        try:
            statement = select(Transaction).where(
                Transaction.type == TransactionType.DEPOSIT,
                or_(
                    Transaction.external_reference == reference_str,
                    Transaction.payment_reference == reference_str
                )
            )
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed deposit reference mapping lookup for reference {reference_str}: {error}")
            raise error

    async def pending_deposits(self, limit: int = 100, offset: int = 0) -> Sequence[Transaction]:
        """Pulls a collection containing all incomplete payment validation entries."""
        return await self.filter(type=TransactionType.DEPOSIT, status=TransactionStatus.PENDING)

    async def successful_deposits(self, limit: int = 100, offset: int = 0) -> Sequence[Transaction]:
        """Pulls a collection containing all verified settlement entries."""
        return await self.filter(type=TransactionType.DEPOSIT, status=TransactionStatus.SUCCESS)

    async def failed_deposits(self, limit: int = 100, offset: int = 0) -> Sequence[Transaction]:
        """Pulls a collection containing all broken or rejected payment validation entries."""
        return await self.filter(type=TransactionType.DEPOSIT, status=TransactionStatus.FAILED)

    # --- Withdrawals Subsystem ---

    async def create_withdrawal(self, user_id: int, wallet_id: int, amount: Decimal, fee: Decimal, destination_details: str) -> Transaction:
        """Registers a pending cash extraction request entry within the immutable ledger.

        Requires an explicit upfront allocation reduction from available wallet balances.
        """
        net_amount = amount - fee
        payload = {
            "user_id": user_id,
            "wallet_id": wallet_id,
            "type": TransactionType.WITHDRAW,
            "status": TransactionStatus.PENDING,
            "amount": amount,
            "fee": fee,
            "net_amount": net_amount,
            "destination": destination_details,
            "description": f"Withdrawal request processing queue: ₦{amount:,.2f}"
        }
        return await self.create(payload, auto_commit=False)

    async def pending_withdrawals(self) -> Sequence[Transaction]:
        """Pulls a collection containing all unfulfilled corporate settlement extractions."""
        return await self.filter(type=TransactionType.WITHDRAW, status=TransactionStatus.PENDING)

    async def approved_withdrawals(self) -> Sequence[Transaction]:
        """Pulls a collection tracking processing operational items within external systems."""
        return await self.filter(type=TransactionType.WITHDRAW, status=TransactionStatus.PROCESSING)

    async def rejected_withdrawals(self) -> Sequence[Transaction]:
        """Pulls a collection tracking canceled or administrative denied payout events."""
        return await self.filter(type=TransactionType.WITHDRAW, status=TransactionStatus.CANCELLED)

    async def completed_withdrawals(self) -> Sequence[Transaction]:
        """Pulls a collection tracking completed bank network payout sequences."""
        return await self.filter(type=TransactionType.WITHDRAW, status=TransactionStatus.SUCCESS)

    # --- Transaction Ledger Engine ---

    async def create_transaction(self, payload: dict[str, Any]) -> Transaction:
        """Persists a custom transaction instance directly onto the ledger tracking systems."""
        return await self.create(payload, auto_commit=False)

    async def get_transaction(self, tx_uuid: str) -> Transaction | None:
        """Fetches an isolated unique record mapping directly to its cryptographic descriptor."""
        try:
            statement = select(Transaction).where(Transaction.transaction_id == tx_uuid)
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed transaction lookup for token identity {tx_uuid}: {error}")
            raise error

    async def transaction_history(self, limit: int = 50, offset: int = 0) -> Sequence[Transaction]:
        """Returns systemic chronological accounting views mapping across all runtime entities."""
        try:
            statement = select(Transaction).order_by(desc(Transaction.created_at)).offset(offset).limit(limit)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed transaction systemic ledger history extraction sequence: {error}")
            raise error

    async def latest_transactions(self, limit_count: int = 10) -> Sequence[Transaction]:
        """Returns the high priority localized timeline slice tracking the latest entries."""
        try:
            statement = select(Transaction).order_by(desc(Transaction.created_at)).limit(limit_count)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed processing top ledger slice retrieval limit {limit_count}: {error}")
            raise error

    async def user_transactions(self, user_id: int, limit: int = 20, offset: int = 0) -> Sequence[Transaction]:
        """Pulls user-isolated ledger histories tracking accounting balances."""
        try:
            statement = (
                select(Transaction)
                .where(Transaction.user_id == user_id)
                .order_by(desc(Transaction.created_at))
                .offset(offset)
                .limit(limit)
            )
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed historical ledger extraction for target user identity node {user_id}: {error}")
            raise error

    # --- Pessimistic Isolation Wallet Engine ---

    async def _get_wallet_locked(self, wallet_id: int) -> Wallet:
        """Pessimistically obtains exclusive write locks blocking simultaneous competing mutations."""
        statement = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        result: Result = await self.session.execute(statement)
        wallet = result.scalar_or_none()
        if not wallet:
            raise ValueError(f"Target system critical wallet instance missing on allocation index lookup: {wallet_id}")
        if wallet.is_locked:
            raise RuntimeError(f"Administrative lockdown operational barrier active on target wallet index: {wallet_id}")
        return wallet

    async def credit_wallet(self, wallet_id: int, amount: Decimal, field_target: str = "available_balance") -> Wallet:
        """Atomically locks the target wallet and increments the designated balance pool."""
        try:
            wallet = await self._get_wallet_locked(wallet_id)
            current_val = getattr(wallet, field_target, Decimal("0.00"))
            setattr(wallet, field_target, current_val + amount)
            
            if field_target == "available_balance":
                wallet.total_deposit += amount
                
            wallet.last_transaction_at = datetime.now(UTC)
            await self.session.flush()
            return wallet
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed credit wallet assignment on index {wallet_id}: {error}")
            await self.session.rollback()
            raise error

    async def debit_wallet(self, wallet_id: int, amount: Decimal, field_target: str = "available_balance") -> Wallet:
        """Atomically locks the target wallet and decrements the designated balance pool."""
        try:
            wallet = await self._get_wallet_locked(wallet_id)
            current_val = getattr(wallet, field_target, Decimal("0.00"))
            
            if current_val < amount:
                raise ValueError(f"Insufficient funds processing transactional deduction on field {field_target}. Available: {current_val}, Requested: {amount}")
                
            setattr(wallet, field_target, current_val - amount)
            
            if field_target == "available_balance":
                wallet.total_withdraw += amount
                
            wallet.last_transaction_at = datetime.now(UTC)
            await self.session.flush()
            return wallet
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed debit wallet assignment on index {wallet_id}: {error}")
            await self.session.rollback()
            raise error

    async def freeze_balance(self, wallet_id: int, amount: Decimal) -> Wallet:
        """Moves designated liquid assets directly into cold storage isolation scopes."""
        try:
            wallet = await self._get_wallet_locked(wallet_id)
            if wallet.available_balance < amount:
                raise ValueError("Insufficient liquid balances matching requested freezing containment constraints.")
                
            wallet.available_balance -= amount
            wallet.frozen_balance += amount
            wallet.last_transaction_at = datetime.now(UTC)
            await self.session.flush()
            return wallet
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed operational freeze execution on index {wallet_id}: {error}")
            await self.session.rollback()
            raise error

    async def unfreeze_balance(self, wallet_id: int, amount: Decimal) -> Wallet:
        """Restores restricted isolation assets back directly to active liquid scopes."""
        try:
            wallet = await self._get_wallet_locked(wallet_id)
            if wallet.frozen_balance < amount:
                raise ValueError("Requested asset extraction size exceeds current isolated frozen allocation boundaries.")
                
            wallet.frozen_balance -= amount
            wallet.available_balance += amount
            wallet.last_transaction_at = datetime.now(UTC)
            await self.session.flush()
            return wallet
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed operational unfreeze execution on index {wallet_id}: {error}")
            await self.session.rollback()
            raise error

    async def transfer_between_balances(self, wallet_id: int, amount: Decimal, source_field: str, destination_field: str) -> Wallet:
        """Performs precise atomic structural reallocation events between localized balances."""
        try:
            wallet = await self._get_wallet_locked(wallet_id)
            source_val = getattr(wallet, source_field, Decimal("0.00"))
            dest_val = getattr(wallet, destination_field, Decimal("0.00"))
            
            if source_val < amount:
                raise ValueError(f"Insufficient asset balances inside source location structural element {source_field}.")
                
            setattr(wallet, source_field, source_val - amount)
            setattr(wallet, destination_field, dest_val + amount)
            wallet.last_transaction_at = datetime.now(UTC)
            await self.session.flush()
            return wallet
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed atomic partition relocation sequence on internal wallet index {wallet_id}: {error}")
            await self.session.rollback()
            raise error

    # --- Capital Investments Framework ---

    async def create_investment(self, payload: dict[str, Any]) -> Investment:
        """Registers a newly locked user asset placement tracker item within the engine."""
        try:
            investment = Investment(**payload)
            self.session.add(investment)
            await self.session.flush()
            return investment
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed to instantiate active investment asset record tracking nodes: {error}")
            await self.session.rollback()
            raise error

    async def active_investments(self) -> Sequence[Investment]:
        """Pulls a listing aggregation of all running accrual configurations."""
        try:
            statement = select(Investment).where(Investment.status == "ACTIVE")
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed compilation tracking listing on active capital allocations: {error}")
            raise error

    async def completed_investments(self) -> Sequence[Investment]:
        """Pulls a listing aggregation of all matured and completed allocations."""
        try:
            statement = select(Investment).where(Investment.status == "COMPLETED")
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed compilation tracking listing on finalized capital allocations: {error}")
            raise error

    async def calculate_daily_profit(self, investment_id: int) -> Decimal:
        """Computes current epoch payouts matching target rule configurations."""
        try:
            statement = select(Investment).where(Investment.id == investment_id)
            result: Result = await self.session.execute(statement)
            investment = result.scalar_or_none()
            if not investment or investment.status != "ACTIVE":
                return Decimal("0.00")
            return (investment.invested_amount * investment.daily_profit_percent) / Decimal("100.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed analytical daily yield estimation sequence on index {investment_id}: {error}")
            raise error

    async def mature_investments(self) -> int:
        """Scans timelines, closing out tracking parameters for investments crossing maturity targets."""
        now = datetime.now(UTC)
        try:
            statement = (
                update(Investment)
                .where(Investment.status == "ACTIVE", Investment.end_date <= now)
                .values(status="COMPLETED", completed_at=now, remaining_days=0)
            )
            result = await self.session.execute(statement)
            await self.session.flush()
            return result.rowcount or 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed systematic automated investment tracking maturity sweep: {error}")
            await self.session.rollback()
            raise error

    # --- Affiliate Bonus Subsystem ---

    async def pay_referral_bonus(self, user_id: int, wallet_id: int, amount: Decimal, from_user_id: int, level: int) -> Transaction:
        """Executes a structured downline network milestone reward inside the transaction ledger framework."""
        payload = {
            "user_id": user_id,
            "wallet_id": wallet_id,
            "type": TransactionType.REFERRAL_REWARD,
            "status": TransactionStatus.SUCCESS,
            "amount": amount,
            "fee": Decimal("0.00"),
            "net_amount": amount,
            "source": f"U-{from_user_id}",
            "description": f"Level {level} Affiliate Commission allocation from partner tracking index: {from_user_id}",
            "completed_at": datetime.now(UTC),
            "processed_at": datetime.now(UTC)
        }
        transaction = await self.create(payload, auto_commit=False)
        await self.credit_wallet(wallet_id, amount, "referral_balance")
        return transaction

    async def referral_reward_history(self, user_id: int) -> Sequence[Transaction]:
        """Pulls transaction collections containing historical network payouts for a user profile."""
        try:
            statement = (
                select(Transaction)
                .where(Transaction.user_id == user_id, Transaction.type == TransactionType.REFERRAL_REWARD)
                .order_by(desc(Transaction.created_at))
            )
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed affiliate reward ledger selection history for identifier {user_id}: {error}")
            raise error

    # --- Analytical Telemetry & Corporate Metrics Summaries ---

    async def total_deposit_volume(self) -> Decimal:
        """Assembles cumulative total volume values representing incoming settlement entries."""
        try:
            statement = select(func.sum(Transaction.net_amount)).where(
                Transaction.type == TransactionType.DEPOSIT,
                Transaction.status == TransactionStatus.SUCCESS
            )
            result = await self.session.execute(statement)
            return Decimal(result.scalar() or "0.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed total incoming processing asset validation compute: {error}")
            raise error

    async def total_withdraw_volume(self) -> Decimal:
        """Assembles cumulative total volume values representing settled corporate extractions."""
        try:
            statement = select(func.sum(Transaction.amount)).where(
                Transaction.type == TransactionType.WITHDRAW,
                Transaction.status == TransactionStatus.SUCCESS
            )
            result = await self.session.execute(statement)
            return Decimal(result.scalar() or "0.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed total outbound processing extraction volume compute: {error}")
            raise error

    async def total_profit_paid(self) -> Decimal:
        """Assembles cumulative total volume values representing daily yield event completions."""
        try:
            statement = select(func.sum(Transaction.amount)).where(
                Transaction.type == TransactionType.DAILY_PROFIT,
                Transaction.status == TransactionStatus.SUCCESS
            )
            result = await self.session.execute(statement)
            return Decimal(result.scalar() or "0.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed systemic absolute profit yield compilation compute: {error}")
            raise error

    async def total_referral_paid(self) -> Decimal:
        """Assembles cumulative total volume values representing complete marketing downline payouts."""
        try:
            statement = select(func.sum(Transaction.amount)).where(
                Transaction.type == TransactionType.REFERRAL_REWARD,
                Transaction.status == TransactionStatus.SUCCESS
            )
            result = await self.session.execute(statement)
            return Decimal(result.scalar() or "0.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed systemic absolute affiliate reward compilation compute: {error}")
            raise error

    async def platform_balance(self) -> Decimal:
        """Aggregates all systemic liquid and frozen cash records directly from the database vaults."""
        try:
            statement = select(func.sum(Wallet.available_balance + Wallet.frozen_balance + Wallet.investment_balance))
            result = await self.session.execute(statement)
            return Decimal(result.scalar() or "0.00")
        except exc.SQLAlchemyError as error:
            logger.error(f"Failed aggregate corporate liability ledger computation: {error}")
            raise error
