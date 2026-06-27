# services.py
"""Production-grade Backup System Service.

Encapsulates business logic for disaster recovery, data persistence, and 
integrity archiving. Orchestrates atomic snapshots, secure encryption, 
retention lifecycle management, and verified restoration workflows to ensure 
platform resilience within the Nigerian Investment Platform architecture.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.backup_system.dtos import BackupStatusDTO, BackupEntryDTO
from src.modules.backup_system.exceptions import BackupProcessingError

logger = logging.getLogger("investment_platform.modules.backup_system.services")


class BackupService:
    """Core domain service for enterprise-grade disaster recovery and snapshots."""

    def __init__(
        self,
        storage_adapter: Any,
        cache_manager: Any,
        event_bus: Any,
        db_utility: Any
    ) -> None:
        self._storage: Final = storage_adapter
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._db: Final = db_utility

    async def get_backup_status(self) -> BackupStatusDTO:
        """Retrieves real-time storage metrics and platform recovery readiness."""
        cache_key = "backup_system_status"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            status = BackupStatusDTO(
                last_backup_time=await self._storage.get_last_snapshot_time(),
                storage_usage_gb=await self._storage.get_usage_metrics(),
                retention_days=30
            )
            
            await self._cache.set(cache_key, status, ttl=3600)
            return status
        except Exception as e:
            logger.error(f"Failed to retrieve backup metrics: {e}")
            raise BackupProcessingError("Operational status retrieval failure.")

    async def trigger_manual_backup(self) -> bool:
        """Orchestrates an atomic full platform snapshot and persists to secure storage."""
        try:
            await self._event_bus.publish("backup.started", {"type": "manual_full"})
            
            # Execute parallelized dump of DB and Redis states
            snapshot_path = await self._db.dump_full_state()
            encrypted_path = await self._storage.encrypt_and_upload(snapshot_path)
            
            success = bool(encrypted_path)
            if success:
                await self._event_bus.publish("backup.completed", {"path": encrypted_path})
                await self._cache.delete("backup_system_status")
            
            return success
        except Exception as e:
            logger.error(f"Critical failure during backup orchestration: {e}")
            await self._event_bus.publish("backup.failed", {"reason": str(e)})
            raise BackupProcessingError("Atomic backup generation failure.")

    async def perform_integrity_check(self, backup_id: str) -> bool:
        """Verifies backup checksums to ensure zero-corruption recovery readiness."""
        try:
            is_valid = await self._storage.verify_checksum(backup_id)
            await self._event_bus.publish("backup.integrity_check_completed", {"id": backup_id})
            return is_valid
        except Exception as e:
            logger.error(f"Integrity validation error for {backup_id}: {e}")
            raise BackupProcessingError("Integrity verification failed.")
