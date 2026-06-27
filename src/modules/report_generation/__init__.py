# __init__.py
"""Report Generation Module Registry.

Aggregates and exposes the public interfaces for the platform's analytical 
reporting and data visualization subsystem. This module provides the 
foundational tools for compiling financial summaries, investment performance 
metrics, and administrative activity logs into structured, exportable 
formats for the Nigerian Investment Platform.
"""

from typing import Final

# Package Public Namespace Interface Definition Manifest
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public report generation components
from src.modules.report_generation.services import ReportGenerationService

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "ReportGenerationService",
]

