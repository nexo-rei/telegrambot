# __init__.py
"""Fraud Security Module Registry.

Aggregates and exposes the public interfaces for the platform's automated 
threat detection, risk assessment, and fraud mitigation subsystem. This module 
provides the defensive infrastructure for heuristic analysis, account protection, 
and suspicious activity monitoring within the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public fraud security components
from src.modules.fraud_security.handlers import FraudSecurityHandlers
from src.modules.fraud_security.services import FraudSecurityService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "FraudSecurityHandlers",
    "FraudSecurityService",
]
