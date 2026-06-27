# redis.py
"""Redis Configuration Engine.

Constructs, structures, and exports performance tuning configurations for the 
centralized memory infrastructure layer (handling Bot FSM, Caching, Session Management, 
Rate Limiting, Celery Brokerage, and Distributed Locks).
"""

from typing import Any, Dict
from config.base import settings


def _build_redis_url(database_index: int) -> str:
    """Constructs an enterprise-grade RFC-compliant Redis URI dynamically.

    Handles explicit baseline authentication paths securely based on raw values.
    """
    auth_prefix = ""
    if settings.redis.PASSWORD:
        auth_prefix = f":{settings.redis.PASSWORD}@"
    
    # Defaults to standalone secure transmission layer mapping
    protocol = "redis"
    
    return f"{protocol}://{auth_prefix}{settings.redis.HOST}:{settings.redis.PORT}/{database_index}"


# 1. Export Declarative Dynamic Infrastructure URI Paths
REDIS_URL: str = _build_redis_url(settings.redis.DB)


class RedisConfig:
    """Production-ready static parameters matrix configuring Redis driver connection pooling.

    Tailored to prevent memory exhaustion, connection leaks, and socket blocking under 
    heavy processing bursts (100,000+ users).
    """

    # Primary Targeting Topology
    HOST: str = settings.redis.HOST
    PORT: int = settings.redis.PORT
    PASSWORD: str | None = settings.redis.PASSWORD
    DEFAULT_DB: int = settings.redis.DB

    # Network Socket Lifecycle Tuning
    SOCKET_TIMEOUT_SECONDS: float = 5.0
    CONNECT_TIMEOUT_SECONDS: float = 10.0
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    
    # Keep-Alive Engine Settings
    SOCKET_KEEPALIVE_OPTIONS: Dict[str, Any] = {
        "keepalive": True,
        "keepalive_options": {
            1: 60,   # TCP_KEEPIDLE: Start pinging after 60 seconds of inactivity
            2: 10,   # TCP_KEEPINTVL: Interval between subsequent keepalive pings
            3: 3     # TCP_KEEPCNT: Max dropped pings before marking connection dead
        }
    }

    # High-Throughput Connection Pool Configuration
    POOL_OPTIONS: Dict[str, Any] = {
        "max_connections": 500,
        "timeout": 30.0,
        "retry_on_timeout": True,
        "encoding": "utf-8",
        "decode_responses": True,
    }

    @classmethod
    def get_client_options(cls, database_index: int | None = None) -> Dict[str, Any]:
        """Assembles a secure driver options mapping blueprint for safe initialization pipelines.

        Args:
            database_index: Optional override target to partition logical memory scopes.

        Returns:
            Dict[str, Any]: Initializer keyword arguments compliant with redis-py interfaces.
        """
        target_db = database_index if database_index is not None else cls.DEFAULT_DB
        
        base_options: Dict[str, Any] = {
            "host": cls.HOST,
            "port": cls.PORT,
            "password": cls.PASSWORD,
            "db": target_db,
            "socket_timeout": cls.SOCKET_TIMEOUT_SECONDS,
            "socket_connect_timeout": cls.CONNECT_TIMEOUT_SECONDS,
            "health_check_interval": cls.HEALTH_CHECK_INTERVAL_SECONDS,
            "retry_on_timeout": True,
        }
        
        # Merge advanced pool tuning parameters and keepalive maps safely
        base_options.update(cls.POOL_OPTIONS)
        base_options.update(cls.SOCKET_KEEPALIVE_OPTIONS)
        
        return base_options

    @classmethod
    def get_celery_broker_url(cls) -> str:
        """Derives a dedicated, safe isolated queue broker connection context string."""
        return settings.celery.BROKER_URL

    @classmethod
    def get_celery_backend_url(cls) -> str:
        """Derives a dedicated, safe isolated task storage execution history lookup context string."""
        return settings.celery.RESULT_BACKEND
        
