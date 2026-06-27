# emoji_manager.py
"""UI Premium Dark Theme Emoji Subsystem.

Provides a centralized, production-ready immutable default registry with optional runtime locale
overrides for managing every emoji, icon, and status indicator used across the application.
Ensures consistent visual brand alignment with a high-end, premium dark theme aesthetic.
"""

import logging
from types import MappingProxyType
from typing import Any, Final, Optional

logger = logging.getLogger("investment_platform.ui.emojis")


class EmojiManager:
    """Centralized governance registry managing UI icons, badges, and status metrics."""

    # Enterprise Premium Dark Luxury Aesthetic Presets Registry
    _DEFAULT_REGISTRY: Final[dict[str, dict[str, str]]] = {
        "navigation": {
            "back": "◀️", "home": "🏠", "refresh": "🔄", "close": "❌",
            "next": "▶️", "prev": "◀️", "forward": "⏩", "menu": "🪐"
        },
        "wallet": {
            "balance": "💰", "deposit": "📥", "withdraw": "📤", "ledger": "📑",
            "wallet_locked": "🔒", "wallet_active": "🔓", "currency_ngn": "₦"
        },
        "investment": {
            "plan_core": "📈", "plan_vip": "🔮", "maturity": "⏳", "yield_accrued": "⚡",
            "portfolio": "💼", "analytics": "📊", "growth_trend": "🚀"
        },
        "referrals": {
            "network_tree": "👥", "affiliate_link": "🔗", "commission": "💎", "rank_up": "👑"
        },
        "notifications": {
            "broadcast": "📢", "alert_urgent": "🚨", "system_message": "💬", "security_audit": "🛡️"
        },
        "support": {
            "ticket_open": "🎫", "agent_resolved": "👨‍💻", "help_desk": "📞"
        },
        "status": {
            "success": "✅", "error": "🛑", "warning": "⚠️", "info": "ℹ️",
            "loading_frame": "⏳", "maintenance_lock": "⚙️", "checkpoint": "▪️"
        },
        "rewards": {
            "checkin_claim": "📆", "gift_code": "🎁", "bonus_payout": "🎉"
        }
    }

    def __init__(self) -> None:
        """Initializes structural fast lookup maps and runtime configuration containers."""
        # Wrap default baseline registry with structural read-only proxy protection
        self._immutable_base: Final[MappingProxyType[str, dict[str, str]]] = MappingProxyType(self._DEFAULT_REGISTRY)
        
        # Runtime locale overrides and dynamic fast lookup matrices
        self._locale_overrides: dict[str, dict[str, str]] = {}
        self._flattened_lookup_cache: dict[str, str] = {}
        
        self._rebuild_lookup_tables()

    def _rebuild_lookup_tables(self) -> None:
        """Recompiles secondary indices to ensure optimized string extraction passes."""
        compiled_lookups: dict[str, str] = {}
        
        # 1. Map defaults into operational space
        for category, sub_map in self._immutable_base.items():
            for alias, emoji in sub_map.items():
                compiled_lookups[f"{category}:{alias}"] = emoji
                compiled_lookups[alias] = emoji  # Direct fallback alias registration

        # 2. Inject active locale overrides to mask primary entries safely
        for category, sub_map in self._locale_overrides.items():
            for alias, emoji in sub_map.items():
                compiled_lookups[f"{category}:{alias}"] = emoji
                compiled_lookups[alias] = emoji

        self._flattened_lookup_cache = compiled_lookups
        logger.debug("Emoji subsystem lookup matrices recompiled successfully.")

    # --- Structural Registry Management API ---

    def register_locale_override(self, category: str, alias: str, custom_emoji: str) -> None:
        """Injects custom visual overrides into tracking scopes to adapt theme parameters.

        Args:
            category: Namespace grouping (e.g., wallet, status, navigation).
            alias: Target configuration lookup string identifier token.
            custom_emoji: Target glyph string character payload.
        """
        if not category or not alias or not custom_emoji.strip():
            raise ValueError("Invalid parameters rejected by emoji configuration manager bounds.")
            
        if category not in self._locale_overrides:
            self._locale_overrides[category] = {}
            
        self._locale_overrides[category][alias] = custom_emoji.strip()
        self._rebuild_lookup_tables()
        logger.info(f"Custom emoji path applied successfully: '{category}:{alias}' -> {custom_emoji}")

    def lookup_emoji(self, identifier: str, fallback: str = "") -> str:
        """Resolves an icon payload string using unified alias indexing metrics.

        Args:
            identifier: Combined routing path key ("wallet:currency_ngn") or singular alias name ("currency_ngn").
            fallback: Default rendering string returned if matches are missing.
        """
        return self._flattened_lookup_cache.get(identifier, fallback)

    # --- Interactive Layout Presentation Formatting Helpers ---

    def prefix_icon(self, base_text: str, emoji_identifier: str) -> str:
        """Prepends a targeted structural glyph safely onto visual text parameters."""
        icon = self.lookup_emoji(emoji_identifier)
        return f"{icon} {base_text}" if icon else base_text

    def suffix_icon(self, base_text: str, emoji_identifier: str) -> str:
        """Appends a targeted structural glyph safely onto visual text parameters."""
        icon = self.lookup_emoji(emoji_identifier)
        return f"{base_text} {icon}" if icon else base_text

    def generate_progress_bar(self, completed: int, absolute_total: int, bar_length: int = 10) -> str:
        """Compiles standard dynamic dark theme tracking metrics indicators.

        Args:
            completed: Current numerical points tracking progress layers.
            absolute_total: Target threshold representing absolute operational completion.
            bar_length: Sizing limit parameter indicating total rendered characters block widths.
        """
        if absolute_total <= 0:
            return "<code>[▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️]</code>"
            
        ratio = max(0.0, min(1.0, completed / absolute_total))
        fill_count = int(ratio * bar_length)
        empty_count = bar_length - fill_count
        
        # Use premium styling layout components for tracking metrics
        fill_glyph = self.lookup_emoji("yield_accrued", "⚡")
        empty_glyph = self.lookup_emoji("checkpoint", "▪️")
        
        bar_layout = (fill_glyph * fill_count) + (empty_glyph * empty_count)
        percentage = int(ratio * 100)
        
        return f"<code>[{bar_layout}]</code> <b>{percentage}%</b>"

    def generate_trend_indicator(self, numeric_variance: float) -> str:
        """Evaluates numerical variance indicators to select corresponding market arrows."""
        if numeric_variance > 0:
            return "🔺"
        if numeric_variance < 0:
            return "🔻"
        return "🔹"
