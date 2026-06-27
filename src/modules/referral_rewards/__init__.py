# __init__.py
"""Referral Rewards Module Registry.

Aggregates and exposes the public interfaces for the platform's referral 
reward allocation subsystem. This module manages the logic for calculating, 
validating, and triggering the distribution of affiliate bonuses based on 
successful investment conversions within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public referral reward components
from src.modules.referral_rewards.handlers import ReferralRewardHandlers
from src.modules.referral_rewards.services import ReferralRewardService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "ReferralRewardHandlers",
    "ReferralRewardService",
]

