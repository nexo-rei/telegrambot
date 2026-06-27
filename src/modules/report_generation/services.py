# services.py
"""Production-grade Report Generation Service.

Encapsulates business logic for high-fidelity financial reporting, analytical 
data aggregation, and regulatory export generation. Orchestrates complex 
queries across repository layers, ensures decimal-precision integrity for 
investment data, and manages secure, cached delivery of reports across 
multiple formats within the platform.
"""

import logging
from typing import Final, Any
from decimal import Decimal
from datetime import datetime

from src.modules.report_generation.dtos import ReportMetadataDTO, ReportRequestDTO
from src.modules.report_generation.exceptions import ReportGenerationError

logger = logging.getLogger("investment_platform.modules.report_generation.services")


class ReportGenerationService:
    """Core domain service for enterprise financial and operational reporting."""

    def __init__(
        self,
        financial_repo: Any,
        user_repo: Any,
        cache_manager: Any,
        event_bus: Any,
        exporter: Any
    ) -> None:
        self._fin_repo: Final = financial_repo
        self._user_repo: Final = user_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._exporter: Final = exporter

    async def generate_financial_statement(
        self, user_id: int, request: ReportRequestDTO
    ) -> ReportMetadataDTO:
        """Compiles an atomic financial statement for a user within a specific timeframe."""
        try:
            # Aggregate financial data with precision
            transactions = await self._fin_repo.get_transactions_by_range(
                user_id, request.start_date, request.end_date
            )
            
            balance_snapshot = await self._fin_repo.get_balance_snapshot(user_id)
            
            # Construct report data structure
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "transactions": transactions,
                "closing_balance": balance_snapshot
            }
            
            # Export to requested format (e.g., PDF/CSV)
            export_path = await self._exporter.create_export(
                report_data, format=request.export_format
            )
            
            metadata = ReportMetadataDTO(
                report_id=f"fin_{user_id}_{datetime.now().timestamp()}",
                path=export_path,
                generated_by=user_id
            )
            
            await self._event_bus.publish("report.financial_statement_generated", {"id": metadata.report_id})
            return metadata
            
        except Exception as e:
            logger.error(f"Financial statement generation failed for {user_id}: {e}")
            raise ReportGenerationError("Financial report compilation failure.")

    async def get_cached_report(self, report_id: str) -> Any:
        """Retrieves a previously generated report from the high-speed cache."""
        try:
            return await self._cache.get(f"report:{report_id}")
        except Exception as e:
            logger.error(f"Cache retrieval error for {report_id}: {e}")
            return None

    async def generate_platform_summary(self) -> dict[str, Decimal]:
        """Aggregates executive-level platform performance metrics."""
        cache_key = "platform_summary_report"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            summary = await self._fin_repo.get_platform_wide_metrics()
            await self._cache.set(cache_key, summary, ttl=1800)
            return summary
        except Exception as e:
            logger.error(f"Platform summary generation failed: {e}")
            raise ReportGenerationError("Executive report generation failure.")
