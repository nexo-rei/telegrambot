# services.py
"""Production-grade Media Manager Service.

Encapsulates business logic for high-performance multimedia processing, 
transcoding, and metadata orchestration. Integrates with FFmpeg for 
heavy-duty media optimization and coordinates with distributed object storage 
and caching backends to ensure scalable, low-latency delivery of assets 
across the investment platform.
"""

import logging
from typing import Final, Any, Optional
from datetime import datetime

from src.modules.media_manager.dtos import MediaMetadataDTO, MediaStatsDTO
from src.modules.media_manager.exceptions import MediaProcessingError

logger = logging.getLogger("investment_platform.modules.media_manager.services")


class MediaManagerService:
    """Core domain service for media lifecycle management and transcoding."""

    def __init__(
        self,
        storage_service: Any,
        ffmpeg_wrapper: Any,
        cache_manager: Any,
        event_bus: Any,
        meta_repo: Any
    ) -> None:
        self._storage: Final = storage_service
        self._ffmpeg: Final = ffmpeg_wrapper
        self._cache: Final = cache_manager
        self._event_bus: Final = event_bus
        self._repo: Final = meta_repo

    async def process_media(
        self, 
        file_id: str, 
        media_type: str, 
        user_id: int
    ) -> MediaMetadataDTO:
        """Orchestrates ingestion, metadata extraction, and optimized processing."""
        try:
            # Generate metadata and trigger optimization workflow
            raw_metadata = await self._ffmpeg.extract_metadata(file_id)
            
            # Perform optimization (transcoding/thumbnailing)
            processed_path = await self._ffmpeg.optimize(file_id, media_type)
            
            metadata = MediaMetadataDTO(
                file_id=file_id,
                codec_info=raw_metadata.get("codec", "unknown"),
                file_size_kb=raw_metadata.get("size", 0) // 1024,
                processed_at=datetime.now()
            )
            
            await self._repo.save_media_metadata(metadata)
            await self._event_bus.publish("media.processed", {"id": file_id})
            
            return metadata
        except Exception as e:
            logger.error(f"Processing error for media {file_id}: {e}")
            raise MediaProcessingError("Automated media optimization failed.")

    async def get_media_statistics(self) -> MediaStatsDTO:
        """Retrieves aggregated library analytics and system processing state."""
        cache_key = "media_stats_summary"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            stats = await self._repo.get_aggregate_stats()
            await self._cache.set(cache_key, stats, ttl=300)
            return stats
        except Exception as e:
            logger.error(f"Media statistics retrieval error: {e}")
            raise MediaProcessingError("Statistical aggregation failure.")

    async def generate_preview(self, file_id: str) -> str:
        """Generates or retrieves a cached preview/thumbnail for UI rendering."""
        cache_key = f"media_preview:{file_id}"
        cached = await self._cache.get(cache_key)
        
        if cached:
            return cached

        try:
            preview_url = await self._ffmpeg.create_thumbnail(file_id)
            await self._cache.set(cache_key, preview_url, ttl=3600)
            return preview_url
        except Exception as e:
            logger.error(f"Thumbnail generation error for {file_id}: {e}")
            raise MediaProcessingError("Preview generation failed.")
