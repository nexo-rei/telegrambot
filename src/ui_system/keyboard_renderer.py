# keyboard_renderer.py
"""UI Keyboard Rendering Engine.

Authoritative button layout manager for the platform. Generates highly optimized,
permission-aware InlineKeyboardMarkup and ReplyKeyboardMarkup matrices. Implements strict
validation against Telegram API limits (e.g., 64-byte callback length limits) and 
hash-based structural caching to eliminate duplicate memory allocations.
"""

import hashlib
import logging
from typing import Any, Final, Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

logger = logging.getLogger("investment_platform.ui.keyboards")

# Telegram API Hard Constraints Matrix
MAX_CALLBACK_DATA_BYTES: Final[int] = 64


class KeyboardValidationError(Exception):
    """Raised when a generated keyboard configuration violates Telegram protocol limits."""
    pass


class KeyboardRenderer:
    """Centralized layout component engine compiling user navigation interfaces."""

    def __init__(self) -> None:
        """Initializes the structure layout allocation matrices and caches."""
        self._keyboard_cache: dict[str, InlineKeyboardMarkup | ReplyKeyboardMarkup] = {}

    def _generate_layout_hash(self, button_matrix: list[list[Any]], structural_salt: str) -> str:
        """Computes a deterministic string signature representing structural keyboard layouts."""
        serialized = f"{str(button_matrix)}:{structural_salt}"
        return hashlib.blake2b(serialized.encode("utf-8"), digest_size=16).hexdigest()

    def _validate_inline_button(self, button: InlineKeyboardButton) -> None:
        """Enforces physical protocol compatibility checks directly on compiled components."""
        if button.callback_data and len(button.callback_data.encode("utf-8")) > MAX_CALLBACK_DATA_BYTES:
            error_msg = (
                f"Telegram structural limit breached. Callback token payload exceeds "
                f"{MAX_CALLBACK_DATA_BYTES} bytes boundary: '{button.callback_data}'"
            )
            logger.error(error_msg)
            raise KeyboardValidationError(error_msg)

    # --- Structural Layout Matrix Orchestrator ---

    def compile_inline_grid(
        self, 
        raw_buttons: list[InlineKeyboardButton], 
        columns: int = 2,
        header_row: Optional[list[InlineKeyboardButton]] = None,
        footer_row: Optional[list[InlineKeyboardButton]] = None,
        use_cache: bool = True
    ) -> InlineKeyboardMarkup:
        """Balances list configurations into explicit multi-column grid tracking arrays.

        Args:
            raw_buttons: Flatted sequence arrays containing target button entities.
            columns: Targeted vertical sizing distribution limits.
            header_row: Optional horizontal row pinned above calculated matrix rows.
            footer_row: Optional horizontal row pinned below calculated matrix rows.
            use_cache: Activates structural identity matching lookups if True.
        """
        grid_matrix: list[list[InlineKeyboardButton]] = []

        if header_row:
            for btn in header_row:
                self._validate_inline_button(btn)
            grid_matrix.append(header_row)

        current_row: list[InlineKeyboardButton] = []
        for button in raw_buttons:
            self._validate_inline_button(button)
            current_row.append(button)
            if len(current_row) == columns:
                grid_matrix.append(current_row)
                current_row = []
        if current_row:
            grid_matrix.append(current_row)

        if footer_row:
            for btn in footer_row:
                self._validate_inline_button(btn)
            grid_matrix.append(footer_row)

        if not grid_matrix:
            raise KeyboardValidationError("Refusing to render empty or zero-element inline layout configurations.")

        if use_cache:
            layout_key = self._generate_layout_hash(grid_matrix, "inline")
            if layout_key in self._keyboard_cache:
                cached_layout = self._keyboard_cache[layout_key]
                if isinstance(cached_layout, InlineKeyboardMarkup):
                    return cached_layout

            compiled = InlineKeyboardMarkup(inline_keyboard=grid_matrix)
            self._keyboard_cache[layout_key] = compiled
            return compiled

        return InlineKeyboardMarkup(inline_keyboard=grid_matrix)

    # --- Reusable Context Utility Constructors ---

    def build_navigation_footer(self, prefix: str) -> list[InlineKeyboardButton]:
        """Assembles the default standard horizontal tracking panel injected across layers."""
        return [
            InlineKeyboardButton(text="◀️ Back", callback_data=f"{prefix}:nav_back"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data=f"{prefix}:nav_refresh"),
            InlineKeyboardButton(text="🏠 Home", callback_data="ui_navigate_home")
        ]

    def render_confirmation_dialog(self, action_prefix: str, transaction_id: str) -> InlineKeyboardMarkup:
        """Assembles a binary choice transactional matrix to capture user intent securely."""
        buttons = [
            InlineKeyboardButton(text="✅ Confirm Execution", callback_data=f"{action_prefix}:yes:{transaction_id}"),
            InlineKeyboardButton(text="❌ Cancel Operation", callback_data=f"{action_prefix}:no:{transaction_id}")
        ]
        return self.compile_inline_grid(raw_buttons=buttons, columns=2, use_cache=False)

    # --- Domain Domain Menu Aggregations ---

    def render_dashboard_menu(self, user_role: str, has_active_investment: bool) -> InlineKeyboardMarkup:
        """Assembles target main menus mapping operations suited to security clearance flags.

        Args:
            user_role: Domain account validation token (GUEST, USER, VIP, MODERATOR, ADMIN).
            has_active_investment: Conditional visibility toggle adjusting contextual layouts.
        """
        buttons: list[InlineKeyboardButton] = [
            InlineKeyboardButton(text="💳 Wallet Ledger", callback_data="menu:wallet"),
            InlineKeyboardButton(text="📈 Capital Plans", callback_data="menu:investments"),
            InlineKeyboardButton(text="👥 Affiliate Tree", callback_data="menu:referrals"),
            InlineKeyboardButton(text="🎫 Support Desk", callback_data="menu:tickets")
        ]

        if has_active_investment:
            buttons.append(InlineKeyboardButton(text="📊 Yield Analytics 📈", callback_data="menu:yield_metrics"))

        footer = []
        if user_role.upper() in ("ADMIN", "SUPERADMIN"):
            footer.append(InlineKeyboardButton(text="⚙️ Admin Command Core ⚙️", callback_data="admin:dashboard"))
        elif user_role.upper() == "MODERATOR":
            footer.append(InlineKeyboardButton(text="🛡️ Moderation Console", callback_data="mod:dashboard"))

        return self.compile_inline_grid(
            raw_buttons=buttons, 
            columns=2, 
            footer_row=footer if footer else None, 
            use_cache=False
        )

    def render_wallet_actions(self, is_wallet_locked: bool) -> InlineKeyboardMarkup:
        """Compiles structural control matrices handling financial liquidity parameters."""
        buttons: list[InlineKeyboardButton] = []
        
        if not is_wallet_locked:
            buttons.extend([
                InlineKeyboardButton(text="📥 Initialize Deposit (Paystack)", callback_data="wallet:deposit"),
                InlineKeyboardButton(text="📤 Process Liquid Extraction", callback_data="wallet:withdraw")
            ])
        else:
            buttons.append(InlineKeyboardButton(text="🔒 Balance Restricted by Admin", callback_data="wallet:locked_noop"))

        buttons.append(InlineKeyboardButton(text="📑 Historical Ledger Statements", callback_data="wallet:statement_page:0"))
        
        return self.compile_inline_grid(
            raw_buttons=buttons, 
            columns=1, 
            footer_row=self.build_navigation_footer("wallet"),
            use_cache=False
        )

    def render_web_app_button(self, button_text: str, interface_url: str) -> InlineKeyboardMarkup:
        """Wraps mini-program runtime connection parameters into functional target components."""
        button = [InlineKeyboardButton(text=button_text, web_app=WebAppInfo(url=interface_url))]
        return InlineKeyboardMarkup(inline_keyboard=[button])

    def render_reply_persistent_menu(self, has_admin_privileges: bool) -> ReplyKeyboardMarkup:
        """Compiles permanent key templates deployed straight into keyboard view frames."""
        layout = [
            [KeyboardButton(text="🪐 Main Dashboard"), KeyboardButton(text="💼 My Portfolio")],
            [KeyboardButton(text="📞 Help & Support"), KeyboardButton(text="⚙️ Preferences")]
        ]
        if has_admin_privileges:
            layout.append([KeyboardButton(text="🛠️ System Metrics Console")])

        return ReplyKeyboardMarkup(
            keyboard=layout,
            resize_keyboard=True,
            persistent=True,
            input_field_placeholder="Select operational vector..."
        )

    # --- Memory Infrastructure Maintenance ---

    def flush_render_cache(self) -> None:
        """Evicts cached matrix structures to reclaim storage allocations."""
        self._keyboard_cache.clear()
        logger.info("Keyboard compiler structural caching boundaries flushed completely.")
