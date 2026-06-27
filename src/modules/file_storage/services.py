# services.py
"""Production-grade File Storage Service.

Encapsulates business logic for distributed object storage, metadata indexing, 
and asset lifecycle management. Provides a unified abstraction layer over 
local filesystems and S3-compatible cloud storage, ensuring atomic operations, 
secure access, and performance-optimized retrieval within the investment platform.
"""

import logging
import uuid
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.file_storage.dtos import FileMetadataDTO, StorageStatsDTO
from src.modules.file_storage.exceptions import FileStorageError

logger = logging.getLogger("investment_platform.modules.file_storage.services")


class FileStorageService:
    """Core domain service for object storage abstraction and asset management."""

    def __init__(
        self,
        storage_adapter: Any,
        meta_repo: Any,
        cache_manager: Any,
        event_bus: Any
    ) -> None:
        self._storage: Final = storage_adapter
        self._repo: Final = meta_repo
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus

    async def store_file(
        self, 
        file_id: str, 
        name: str, 
        owner_id: int,
        content_type: Optional[str] = None
    ) -> FileMetadataDTO:
        """Processes and persists a file, updating metadata and event streams."""
        try:
            # Generate secure path and unique identifier
            unique_name = f"{uuid.uuid4()}_{name}"
            
            # Persist to physical object storage
            storage_path = await self._storage.upload(file_id, unique_name)
            
            metadata = FileMetadataDTO(
                file_id=str(uuid.uuid4()),
                file_name=name,
                file_path=storage_path,
                owner_id=owner_id,
                created_at=datetime.now(),
                content_type=content_type or "application/octet-stream"
            )
            
            await self._repo.save_metadata(metadata)
            await self._cache.delete("storage_stats_summary")
            await self._event_bus.publish("storage.file_uploaded", {"id": metadata.file_id})
            
            return metadata
        except Exception as e:
            logger.error(f"Storage persistence error for user {owner_id}: {e}")
            raise FileStorageError("Failed to store asset in object storage.")

    async def get_storage_statistics(self) -> StorageStatsDTO:
        """Retrieves aggregated storage utilization and quota metrics."""
        cache_key = "storage_stats_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            stats = await self._repo.get_aggregate_usage()
            await self._cache.set(cache_key, stats, ttl=300)
            return stats
        except Exception as e:
            logger.error(f"Storage metrics aggregation error: {e}")
            raise FileStorageError("Statistical report generation failed.")

    async def generate_signed_url(self, file_path: str, ttl_seconds: int = 3600) -> str:
        """Generates a secure, temporary access URL for object retrieval."""
        try:
            return await self._storage.create_presigned_url(file_path, ttl_seconds)
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {file_path}: {e}")
            raise FileStorageError("Secure URL generation failure.")
