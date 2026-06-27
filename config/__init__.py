# __init__.py
"""Configuration module initialization.

Exposes the validated, global settings singleton instance for deterministic
import paths across the enterprise application lifecycle.
"""

from config.base import settings

__all__ = ["settings"]
