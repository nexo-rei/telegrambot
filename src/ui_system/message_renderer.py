# message_renderer.py
"""UI Message Rendering Engine.

Authoritative presentation layer driver for building, transmitting, and maintaining
stateful lifecycle tracks over chat communications. Incorporates localized HTML parsing,
inplace update heuristics, automatic rate mitigation blocks, and structural metadata 
caching to guarantee a clean transactional interface profile.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, UTC
from typing import Any, Dict, Final, List, Optional

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup

logger = logging.getLogger("investment_platform.ui.messages")


class RenderedMessageMetadata:
    """Tracks state signatures, structures, and payload parameters for an active message row."""

    def __init__(
        self,
        chat_id: int,
        message_id: int,
        content_hash: str,
        parse_mode: str,
        reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None,
    ) -> None:
        self.chat_id: Final[int] = chat_id
        self.message_id: Final[int] = message_id
        self.content_hash: str = content_hash
        self.parse_mode: str = parse_mode
        self.reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = reply_markup
        self.rendered_at: datetime = datetime.now(UTC)


class MessageRenderer:
    """Central structural component managing messaging pipelines and UI caching layers."""

    def __init__(self, bot: Bot) -> None:
        """Initializes the layout delivery engine.

        Args:
            bot: Structural client communication link driver config.
        """
        self.bot: Final[Bot] = bot
        self._message_cache: Dict[int, RenderedMessageMetadata] = {}

    def _calculate_payload_hash(self, text: str, markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup]) -> str:
        """Generates an explicit verification key fingerprint to detect template variations."""
        signature = f"{text}:{str(markup)}"
        return hashlib.blake2b(signature.encode("utf-8"), digest_size=16).hexdigest()

    # --- Core Transactional Delivery Systems ---

    async def render_text_message(
        self,
        chat_id: int,
        text_content: str,
        reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None,
        parse_mode: str = ParseMode.HTML,
        force_new_node: bool = False,
    ) -> Optional[Message]:
        """Dispatches or alters text visual instances efficiently based on payload history traces.

        Args:
            chat_id: Target subscriber conversation verification reference index.
            text_content: Formatted text payload adhering to the active parse mode constraints.
            reply_markup: Button matrices bound underneath text displays.
            parse_mode: Parsing schema identifier string (HTML, MarkdownV2).
            force_new_node: Prevents evaluation of inplace tracking edits if True.
        """
        current_hash = self._calculate_payload_hash(text_content, reply_markup)
        cached_meta = self._message_cache.get(chat_id)

        # Pathway A: Inplace text mutations for existing display nodes
        if not force_new_node and cached_meta and isinstance(reply_markup, InlineKeyboardMarkup | None):
            if cached_meta.content_hash == current_hash:
                logger.debug(f"Redundant mutation intercepted for chat {chat_id}. Outbound network tasks dropped.")
                return None

            try:
                mutated_msg = await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=cached_meta.message_id,
                    text=text_content,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
                
                cached_meta.content_hash = current_hash
                cached_meta.reply_markup = reply_markup
                cached_meta.rendered_at = datetime.now(UTC)
                
                if isinstance(mutated_msg, Message):
                    return mutated_msg
                return None

            except TelegramBadRequest as error:
                if "message to edit not found" in str(error) or "message is not modified" in str(error):
                    logger.warning(f"Message frame {cached_meta.message_id} detached or invariant. Regenerating line.")
                else:
                    logger.error(f"Inplace layout modification failed: {error}")
            except TelegramRetryAfter as rate_limit:
                logger.warning(f"Rate ceiling hit on branch {chat_id}. Backing off across {rate_limit.retry_after}s.")
                await asyncio.sleep(rate_limit.retry_after)
                return await self.render_text_message(chat_id, text_content, reply_markup, parse_mode, force_new_node)
            except TelegramAPIError as structural_fault:
                logger.error(f"Subsystem exception during message layout transformation: {structural_fault}")
                return None

        # Pathway B: Generative creation of fresh display nodes
        try:
            new_msg = await self.bot.send_message(
                chat_id=chat_id,
                text=text_content,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            
            self._message_cache[chat_id] = RenderedMessageMetadata(
                chat_id=chat_id,
                message_id=new_msg.message_id,
                content_hash=current_hash,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            return new_msg

        except TelegramRetryAfter as rate_limit:
            logger.warning(f"Rate limit hit during generation on {chat_id}. Sleeping {rate_limit.retry_after}s.")
            await asyncio.sleep(rate_limit.retry_after)
            return await self.render_text_message(chat_id, text_content, reply_markup, parse_mode, force_new_node)
        except Exception as serious_error:
            logger.critical(f"Total delivery structural failure on account tracking path {chat_id}: {serious_error}", exc_info=True)
            return None

    async def remove_message_node(self, chat_id: int, target_message_id: Optional[int] = None) -> bool:
        """Removes a target message row from active viewports cleanly.

        Args:
            chat_id: Distinct individual network locator sequence.
            target_message_id: Explicit tracking ID to eliminate. Defaults to the cached reference if empty.
        """
        msg_id = target_message_id
        if not msg_id:
            cached_meta = self._message_cache.get(chat_id)
            if not cached_meta:
                return False
            msg_id = cached_meta.message_id

        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            if not target_message_id or (cached_meta and cached_meta.message_id == target_message_id):
                self._message_cache.pop(chat_id, None)
            return True
        except TelegramBadRequest as error:
            logger.warning(f"Refusing to delete message {msg_id} on {chat_id}. Target may be expired or absent. Context: {error}")
            self._message_cache.pop(chat_id, None)
            return False
        except TelegramAPIError as failure:
            logger.error(f"Failed deleting requested sequence identifier frame: {failure}")
            return False

    # --- Structural Visual Component Compilers ---

    def format_premium_header(self, raw_title: str) -> str:
        """Generates consistent premium branding top text bars for layout structures."""
        return f"<b>┏━━━━━━━━━━━━━━━━━━━━┓</b>\n🌟 <b>{raw_title.strip().upper()}</b>\n<b>┗━━━━━━━━━━━━━━━━━━━━┛</b>\n\n"

    def format_wallet_summary(self, balance_ngn: float, deposit_pending: float, active_yield_accrued: float) -> str:
        """Assembles structured investment statistics formatting blocks aligned with premium themes."""
        layout = (
            f"{self.format_premium_header('Financial Portfolio Summary')}"
            f"💰 Available Capital: <code>₦{balance_ngn:,.2f}</code>\n"
            f"⏳ Pending Reconciliations: <code>₦{deposit_pending:,.2f}</code>\n"
            f"📈 Absolute Yield Dividends: <code>₦{active_yield_accrued:,.2f}</code>\n\n"
            f"<i>Last verified chronological sync: {datetime.now(UTC).strftime('%H:%M:%S')} UTC</i>"
        )
        return layout

    def format_error_banner(self, operational_fault_text: str) -> str:
        """Assembles standard notification block warning states securely."""
        return (
            f"🛑 <b>TRANSACTIONAL ERROR BOUNDARY</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"⚠️ <i>{operational_fault_text}</i>\n\n"
            f"Please fix parameters or contact core systems engineering support desks."
        )

    # --- Operational Cache Maintenance ---

    def clear_historical_caches(self) -> None:
        """Flushes transient memory tracking variables systematically to clear runtime footprints."""
        self._message_cache.clear()
        logger.info("Message renderer metadata cache allocations flushed completely.")
