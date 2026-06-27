# services.py
"""Production-grade Transaction Service.

Encapsulates business logic for retrieving, aggregating, and reporting on 
financial transactions across the platform. Ensures high-performance data 
access through a cache-first strategy while maintaining strict ACID 
consistency for financial auditability and reporting.
"""

import logging
from typing import Final, Any, List
from datetime import datetime

from src.modules.transactions.dtos import TransactionDetailsDTO
from src.shared.utilities.math_precision import PrecisionMath

logger = logging.getLogger("investment_platform.modules.transactions.services")


class TransactionService:
    """Core domain service for ledger management, history, and financial analytics."""

    def __init__(
        self,
        transaction_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._transaction_repo: Final = transaction_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def get_recent_summary(self, user_id: int) -> str:
        """Retrieves and formats a summary of the most recent user transactions."""
        
        cache_key = f"tx_summary_{user_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        transactions = await self._transaction_repo.get_recent(user_id, limit=5)
        
        summary_lines = []
        for tx in transactions:
            timestamp = tx.created_at.strftime("%d-%m %H:%M")
            summary_lines.append(f"[{timestamp}] {tx.type.upper()}: ₦{tx.amount:,.2f}")
            
        result = "\n".join(summary_lines) if summary_lines else "No recent transactions found."
        
        await self._cache.set(cache_key, result, ttl=300)
        await self._event_bus.publish("transaction.viewed", {"user_id": user_id})
        
        return result

    async def get_transaction_details(self, tx_id: str) -> str:
        """Retrieves comprehensive details for a specific transaction record."""
        
        tx = await self._transaction_repo.get_by_id(tx_id)
        if not tx:
            raise ValueError("Transaction record not found.")

        details = (
            f"Type: {tx.type.replace('_', ' ').title()}\n"
            f"Reference: `{tx.reference}`\n"
            f"Amount: ₦{tx.amount:,.2f}\n"
            f"Status: {tx.status.capitalize()}\n"
            f"Date: {tx.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return details

    async def generate_financial_statement(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Any]:
        """Generates a structured list of transactions for a specific period."""
        
        transactions = await self._transaction_repo.get_by_date_range(
            user_id, start_date, end_date
        )
        
        await self._event_bus.publish("statement.generated", {"user_id": user_id})
        return transactions
