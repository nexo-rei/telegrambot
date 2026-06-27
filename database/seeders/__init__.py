# __init__.py
"""Database Seeders Package Registry.

Aggregates and exposes the canonical seeding interfaces for the platform's 
PostgreSQL data layer. This package provides the infrastructure for 
populating initial master data, such as investment plans and configuration 
constants, ensuring consistent environment state for development, testing, 
and production bootstrapping.
"""

from typing import Final

# Package Metadata
__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Velorix Core Architecture Division"
__maintainer__: Final[str] = "Velorix Core Architecture Division"
__license__: Final[str] = "Proprietary / Commercial Enterprise License"

# Explicitly pull public seeding components
from database.seeders.plan_seeder import PlanSeeder

__all__: Final[list[str]] = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__license__",
    "PlanSeeder",
]
