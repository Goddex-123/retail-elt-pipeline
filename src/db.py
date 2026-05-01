"""
Retail ELT Platform — Database Connection Manager
==================================================
Thread-safe connection manager with context manager pattern,
retry logic, and schema management.
"""

import time
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.pool import QueuePool

from src.config import db_config, schema_config
from src.logger import get_logger

logger = get_logger(__name__)

# Module-level engine (lazy singleton)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create a SQLAlchemy engine with connection pooling.

    Returns:
        SQLAlchemy Engine with connection pool.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            db_config.url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )
        logger.info("Database engine created", extra={"host": db_config.host, "database": db_config.database})
    return _engine


@contextmanager
def get_connection(retries: int = 3, delay: float = 2.0) -> Generator[Connection, None, None]:
    """
    Context manager for database connections with retry logic.

    Args:
        retries: Number of retry attempts on connection failure.
        delay: Delay in seconds between retries (exponential backoff).

    Yields:
        Active database connection.
    """
    engine = get_engine()
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                yield conn
                return
        except Exception as e:
            last_error = e
            wait_time = delay * (2 ** (attempt - 1))
            logger.warning(
                f"Connection attempt {attempt}/{retries} failed, retrying in {wait_time}s",
                extra={"error": str(e)},
            )
            if attempt < retries:
                time.sleep(wait_time)

    logger.error(f"All {retries} connection attempts failed", extra={"error": str(last_error)})
    raise last_error


def ensure_schemas() -> None:
    """Create all required database schemas if they don't exist."""
    schemas = [schema_config.source, schema_config.bronze, schema_config.silver, schema_config.gold]

    with get_connection() as conn:
        for schema in schemas:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()
            logger.info(f"Schema ensured: {schema}")


def execute_query(query: str, params: Optional[dict] = None) -> list:
    """
    Execute a SQL query and return results.

    Args:
        query: SQL query string.
        params: Optional query parameters.

    Returns:
        List of result rows.
    """
    with get_connection() as conn:
        result = conn.execute(text(query), params or {})
        if result.returns_rows:
            return [dict(row._mapping) for row in result.fetchall()]
        conn.commit()
        return []
