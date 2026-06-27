# ui_manager.py
"""UI Orchestration Engine.

Authoritative presentation layer driver for the platform, functioning as a single
source of truth for screen rendering, navigational stacks, fluid status indicators,
and dark luxury style enforcement. Optimizes network footprints by parsing state variations
to choose between inplace editing or deletion and new message generation.
"""

import asyncio
import html
import logging
from collections import collections
from collections.abc import Sequence
from datetime import datetime
from enum import Enum
from typing import Any, Final, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramRetryAfter
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)

# Static Visual Assets and Configurations Matrix
DARK_THEME_DIVIDER: Final[str] = "━" * 22
AMETHYST_GLOW: Final[str] = "🔮"
ELECTRIC_BLUE: Final[str] = "⚡"
DARK_CARD_TOP: Final[str] = "┏━━━━━━━━━━━━━━━━━━━━┓"
DARK_CARD_BOTTOM: Final[str] = "┗━━━━━━━━━━━━━━━━━━━━┛"

# Production Animated Sticker File Identifiers (.tgs cloud ids)
STICKER_LOADING: Final[str] = "CAACAgIAAxkBAAEExxxk..." 
STICKER_SUCCESS: Final[str] = "CAACAgIAAxkBAAEEyyyk..."
STICKER_ERROR: Final[str] = "CAACAgIAAxkBAAEEzzzk..."
STICKER_WELCOME: Final[str] = "CAACAgIAAxkBAAEE000k..."
STICKER_PAYMENT: Final[str] = "CAACAgIAAxkBAAEE111k..."

logger = logging.getLogger("investment_platform.ui.manager")


class RenderMode(str, Enum):
    """Directs the transport engine on updating display coordinates."""
    AUTO = "AUTO"
    FORCE_NEW = "FORCE_NEW"
    EDIT_EXISTING = "EDIT_EXISTING"


class UIContext:
    """Isolates unique layout properties and historical vectors for an active participant."""

    def __init__(self, chat_id: int) -> None:
        self.chat_id: int = chat_id
        self.history_stack: list[str] = []
        self.breadcrumbs: list[str] = []
        self.last_message_id: Optional[int] = None
        self.current_screen: Optional[str] = None
        self.previous_screen: Optional[str] = None
        self.current_keyboard: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None


class UIManager:
    """Central structural manager translating application states into interface components."""

    def __init__(self, bot: Bot) -> None:
        """Initializes the view management subsystem.

        Args:
            bot: Active structural client driver configuration wrapper instance.
        """
        self.bot = bot
        self._user_contexts: dict[int, UIContext] = collections.defaultdict(UIContext)

    def get_context(self, chat_id: int) -> UIContext:
        """Locates or binds a running contextual navigation tree state for a target chat partition."""
        if chat_id not in self._user_contexts:
            self._user_contexts[chat_id] = UIContext(chat_id)
        return self._user_contexts[chat_id]

    @staticmethod
    def escape_html_payload(text_raw: str) -> str:
        """Protects formatting boundaries against parsing validation breaks."""
        return html.escape(text_raw)

    def render_premium_card(self, header_title: str, core_content: str, footer_note: Optional[str] = None) -> str:
        """Wraps string parameters inside dark theme design lines.

        Args:
            header_title: Functional string label marking top visual bars.
            core_content: Central transactional text elements payload.
            footer_note: Supplemental compliance tracking signatures.
        """
        clean_title = self.escape_html_payload(header_title.upper())
        layout = (
            f"<code>{DARK_CARD_TOP}</code>\n"
            f"{AMETHYST_GLOW} <b>{clean_title}</b>\n"
            f"<code>{DARK_THEME_DIVIDER}</code>\n\n"
            f"{core_content}\n\n"
        )
        if footer_note:
            layout += f"<code>{DARK_THEME_DIVIDER}</code>\n{ELECTRIC_BLUE} <i>{self.escape_html_payload(footer_note)}</i>\n"
        layout += f"<code>{DARK_CARD_BOTTOM}</code>"
        return layout

    def build_pagination_keyboard(
        self, 
        action_prefix: str, 
        current_page: int, 
        total_pages: int, 
        append_controls: Optional[list[list[InlineKeyboardButton]]] = None
    ) -> InlineKeyboardMarkup:
        """Compiles standard matrix paginating buttons bound to analytical views.

        Args:
            action_prefix: Systemic routing path token injected into callback strings.
            current_page: 0-indexed integer marking local viewing points.
            total_pages: Absolute ceiling indicating total segmented datasets.
            append_controls: Supplementary actionable button lists injected underneath navigation rows.
        """
        buttons: list[InlineKeyboardButton] = []
        
        if current_page > 0:
            buttons.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"{action_prefix}:page:{current_page - 1}"))
        
        buttons.append(InlineKeyboardButton(text=f"▪️ {current_page + 1} / {total_pages} ▪️", callback_data="ui_noop"))
        
        if current_page < total_pages - 1:
            buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"{action_prefix}:page:{current_page + 1}"))

        keyboard_matrix = [buttons]
        
        # Structure core infrastructure utilities layout row
        utility_row = [
            InlineKeyboardButton(text="◀️ Back", callback_data="ui_navigate_back"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data=f"{action_prefix}:refresh"),
            InlineKeyboardButton(text="🏠 Home", callback_data="ui_navigate_home")
        ]
        keyboard_matrix.append(utility_row)

        if append_controls:
            keyboard_matrix.extend(append_controls)

        return InlineKeyboardMarkup(inline_keyboard=keyboard_matrix)

    async def send_animation_scene(self, chat_id: int, animation_type: str) -> Optional[Message]:
        """Dispatches context stickers to emphasize balance mutations or loading tasks.

        Args:
            chat_id: Destination structural unique network location index.
            animation_type: Symbolic taxonomy key mapped to direct sticker cloud file locations.
        """
        sticker_map = {
            "loading": STICKER_LOADING,
            "success": STICKER_SUCCESS,
            "error": STICKER_ERROR,
            "welcome": STICKER_WELCOME,
            "payment": STICKER_PAYMENT,
        }
        file_id = sticker_map.get(animation_type.lower())
        if not file_id:
            logger.warning(f"Requested animation profile matching alias '{animation_type}' was not resolved.")
            return None

        try:
            return await self.bot.send_sticker(chat_id=chat_id, sticker=file_id)
        except TelegramAPIError as error:
            logger.error(f"Failed to dispatch animation sticker token to target target chat tracking index {chat_id}: {error}")
            return None

    async def execute_screen_render(
        self,
        chat_id: int,
        screen_key: str,
        text_payload: str,
        reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None,
        mode: RenderMode = RenderMode.AUTO
    ) -> bool:
        """Directs transport operations to manifest presentation blocks.

        Maintains structural rate compliance and transparent safety fallbacks for modified strings.

        Args:
            chat_id: Target subscriber tracking footprint index.
            screen_key: Domain registry descriptor string naming the active target screen layout.
            text_payload: Assembled text structure layout compliant with HTML parsing requirements.
            reply_markup: Optional inline or reply button controls payload attached to current views.
            mode: Hard configuration flags overriding dynamic inplace editing heuristics.
        """
        context = self.get_context(chat_id)
        target_message_id = context.last_message_id
        is_inline_markup = isinstance(reply_markup, InlineKeyboardMarkup) or reply_markup is None

        # Record navigation trail variables safely
        if context.current_screen != screen_key:
            context.previous_screen = context.current_screen
            context.current_screen = screen_key
            if screen_key not in context.history_stack:
                context.history_stack.append(screen_key)

        # Evaluate constraints determining direct layout transformation properties
        should_edit = (
            mode == RenderMode.EDIT_EXISTING or 
            (mode == RenderMode.AUTO and target_message_id is not None and is_inline_markup)
        )

        if should_edit and target_message_id is not None:
            try:
                await self.bot.edit_message_text(
                    text=text_payload,
                    chat_id=chat_id,
                    message_id=target_message_id,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
                context.current_keyboard = reply_markup
                return True
            except TelegramBadRequest as error:
                if "message is not modified" in str(error):
                    logger.debug(f"Redundant inline display layout call bypassed for tracking index {chat_id}.")
                    return True
                if "message to edit not found" in str(error) or "chat not found" in str(error):
                    logger.warning(f"Inplace edit trace broke against missing message frame {target_message_id}. Falling back to clean delivery.")
                else:
                    logger.error(f"API BadRequest mutation block failure context: {error}")
                    return False
            except TelegramRetryAfter as rate_limit:
                logger.warning(f"Flood ceiling triggered on identity branch {chat_id}. Sleeping across {rate_limit.retry_after}s.")
                await asyncio.sleep(rate_limit.retry_after)
                return await self.execute_screen_render(chat_id, screen_key, text_payload, reply_markup, mode)
            except TelegramAPIError as general_error:
                logger.error(f"Structural driver infrastructure fault inside rendering loop: {general_error}")
                return False

        # Fallback block deploying clean visual tracking items when edits break
        try:
            sent_msg = await self.bot.send_message(
                chat_id=chat_id,
                text=text_payload,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            context.last_message_id = sent_msg.message_id
            context.current_keyboard = reply_markup
            return True
        except TelegramAPIError as absolute_fault:
            logger.critical(f"Total delivery drop encountered generating clear visual frame for identity {chat_id}: {absolute_fault}")
            return False

    async def handle_callback_cleanup(self, query: CallbackQuery) -> bool:
        """Acknowledges incoming queries to eliminate loading state bars on clients.

        Args:
            query: Live interface callback query interaction context.
        """
        try:
            await query.answer()
            return True
        except TelegramAPIError as error:
            logger.error(f"Failed to clear feedback loop state context reference matching payload index {query.id}: {error}")
            return False
