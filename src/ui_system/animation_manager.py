# animation_manager.py
"""UI Visual Animation Subsystem.

Authoritative asset management and execution engine for high-end UI micro-interactions,
Lottie/TGS animated stickers, and cryptographic File ID tracking. Optimizes platform
throughput by verifying local caches before utilizing background multi-part uploads, 
eliminating redundant network operations.
"""

import asyncio
from datetime import datetime, UTC
import logging
from typing import Any, Dict, Final, List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import FSInputFile, Message

logger = logging.getLogger("investment_platform.ui.animations")


class AnimationAsset:
    """Represents a validated graphical visual asset layout entity descriptor."""

    def __init__(self, key: str, local_path: Optional[str] = None, telegram_file_id: Optional[str] = None) -> None:
        self.key: Final[str] = key
        self.local_path: Optional[str] = local_path
        self.telegram_file_id: Optional[str] = telegram_file_id
        self.registered_at: Final[datetime] = datetime.now(UTC)


class AnimationQueueItem:
    """Encapsulates execution configurations for items placed in sequential playback queues."""

    def __init__(self, chat_id: int, animation_key: str, priority: int = 0) -> None:
        self.chat_id: Final[int] = chat_id
        self.animation_key: Final[str] = animation_key
        self.priority: Final[int] = priority
        self.timestamp: Final[datetime] = datetime.now(UTC)


class AnimationManager:
    """Enterprise coordinator managing Lottie (.tgs) assets and transactional loading states."""

    def __init__(self, bot: Bot) -> None:
        """Initializes the animation asset governance registry.

        Args:
            bot: Active structural client communication link wrapper instance.
        """
        self.bot: Final[Bot] = bot
        self._asset_registry: Dict[str, AnimationAsset] = {}
        self._active_queues: Dict[int, List[AnimationQueueItem]] = {}
        self._lock: Final[asyncio.Lock] = asyncio.Lock()

        # Hardwire systemic production defaults maps
        self._initialize_production_presets()

    def _initialize_production_presets(self) -> None:
        """Populates the asset database with default platform tracking pointers."""
        presets = [
            "loading_core", "login_wait", "dashboard_fetch", "wallet_refresh",
            "payment_verify", "investment_activate", "withdrawal_process",
            "referral_calc", "success_generic", "error_generic",
            "payment_success", "payment_failed", "withdrawal_complete",
            "daily_reward", "referral_earned"
        ]
        for preset in presets:
            self.register_animation(AnimationAsset(key=preset))

    # --- Core Asset Registration API ---

    def register_animation(self, asset: AnimationAsset) -> None:
        """Secures an animation asset context directly within the active lookup registry."""
        if not asset or not asset.key:
            raise ValueError("Structural visual asset verification failed against validation rules.")
        self._asset_registry[asset.key] = asset
        logger.debug(f"Animation profile path mapped safely to token descriptor: '{asset.key}'")

    def lookup_asset(self, key: str) -> AnimationAsset:
        """Locates an active graphical profile index or raises clear tracking exceptions."""
        asset = self._asset_registry.get(key)
        if not asset:
            logger.error(f"Asset tracking violation. Animation key '{key}' undefined inside execution tables.")
            raise KeyError(f"Target visual profile resource path missing: '{key}'")
        return asset

    def update_cached_file_id(self, key: str, file_id: str) -> None:
        """Binds a freshly generated Telegram file index hash onto an existing profile metadata node."""
        asset = self.lookup_asset(key)
        asset.telegram_file_id = file_id
        logger.info(f"Synchronized persistent cloud pointer token id for animation: '{key}' -> [{file_id[:15]}...]")

    # --- Transactional Playback Rendering Operations ---

    async def play_sticker_animation(self, chat_id: int, animation_key: str, disable_notification: bool = True) -> Optional[Message]:
        """Dispatches an animated sticker (.tgs) context using efficient identification mechanics.

        Args:
            chat_id: Destination subscriber account communication track index.
            animation_key: Lookup token naming the structural asset layout target.
            disable_notification: Mutes delivery sounds to preserve fluid UX layers.
        """
        async with self._lock:
            try:
                asset = self.lookup_asset(animation_key)
                
                # Pathway A: Instant replication using cloud infrastructure pointers
                if asset.telegram_file_id:
                    try:
                        return await self.bot.send_sticker(
                            chat_id=chat_id,
                            sticker=asset.telegram_file_id,
                            disable_notification=disable_notification
                        )
                    except TelegramAPIError as api_error:
                        logger.warning(f"Cached cloud trace token [{asset.telegram_file_id[:10]}] invalid for chat {chat_id}. Forcing regeneration. Error: {api_error}")
                        asset.telegram_file_id = None

                # Pathway B: Multi-part disk stream resolution fallback
                if not asset.local_path:
                    logger.error(f"Execution boundary fault. Animation asset '{animation_key}' lacks valid local path mappings.")
                    return None

                input_file = FSInputFile(asset.local_path)
                msg = await self.bot.send_sticker(
                    chat_id=chat_id,
                    sticker=input_file,
                    disable_notification=disable_notification
                )
                
                if msg.sticker and msg.sticker.file_id:
                    self.update_cached_file_id(animation_key, msg.sticker.file_id)
                return msg

            except TelegramRetryAfter as backoff:
                logger.warning(f"Flood boundary hit within active visual pipeline on {chat_id}. Delaying execution for {backoff.retry_after}s.")
                await asyncio.sleep(backoff.retry_after)
                return await self.play_sticker_animation(chat_id, animation_key, disable_notification)
            except Exception as structural_fault:
                logger.error(f"Total processing failure dispatching visual frame scene '{animation_key}' to {chat_id}: {structural_fault}", exc_info=True)
                return None

    async def play_video_animation(self, chat_id: int, animation_key: str, caption_text: Optional[str] = None) -> Optional[Message]:
        """Dispatches an MP4 or silent looping visual document stream to the client.

        Args:
            chat_id: Unique user network chat location index.
            animation_key: Lookup key mapping to an explicit file layout structure.
            caption_text: Supplemental string text attached underneath the video window frame.
        """
        try:
            asset = self.lookup_asset(animation_key)
            if asset.telegram_file_id:
                return await self.bot.send_animation(chat_id=chat_id, animation=asset.telegram_file_id, caption=caption_text, parse_mode="HTML")

            if not asset.local_path:
                return None

            input_file = FSInputFile(asset.local_path)
            msg = await self.bot.send_animation(chat_id=chat_id, animation=input_file, caption=caption_text, parse_mode="HTML")
            
            if msg.animation and msg.animation.file_id:
                self.update_cached_file_id(animation_key, msg.animation.file_id)
            return msg
        except Exception as error:
            logger.error(f"Failed handling outbound video loop delivery sequence for '{animation_key}': {error}")
            return None

    # --- Priority Queueing Management Pipelines ---

    async def enqueue_animation_sequence(self, chat_id: int, animation_key: str, priority: int = 0) -> None:
        """Pushes an animation sequence request onto a priority tracking queue frame.

        Args:
            chat_id: Target user conversation identification reference.
            animation_key: System asset key describing the visual element.
            priority: Sorting index allowing urgent alerts to bypass normal processing order.
        """
        if chat_id not in self._active_queues:
            self._active_queues[chat_id] = []
        
        new_item = AnimationQueueItem(chat_id, animation_key, priority)
        queue = self._active_queues[chat_id]
        
        # Insert item and sort by priority descending, then by timestamp ascending
        queue.append(new_item)
        queue.sort(key=lambda x: (-x.priority, x.timestamp))
        logger.debug(f"Animation event successfully queued for channel context {chat_id}: [{animation_key}] Level: {priority}")

    async def process_next_queued_animation(self, chat_id: int) -> Optional[Message]:
        """Pops and executes the highest priority visualization task from the active queue block."""
        queue = self._active_queues.get(chat_id, [])
        if not queue:
            return None
            
        next_item = queue.pop(0)
        if not queue:
            self._active_queues.pop(chat_id, None)
            
        return await self.play_sticker_animation(next_item.chat_id, next_item.animation_key)

    def flush_user_queues(self, chat_id: int) -> None:
        """Evicts pending visuals tracking layers for a specific target conversation."""
        self._active_queues.pop(chat_id, None)
        logger.debug(f"Playback queue pipelines cleared for chat identification branch: {chat_id}")
