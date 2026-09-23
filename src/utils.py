"""
Retail ELT Platform — Common Utilities
=======================================
Shared helper functions used across ingestion,
transformation, and quality modules.
"""

import time
from datetime import datetime, timezone
from functools import wraps
from typing import Callable, Any

from src.logger import get_logger

logger = get_logger(__name__)


def current_utc_timestamp() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def timer(func: Callable) -> Callable:
    """
    Decorator that logs execution duration of a function.

    Usage:
        @timer
        def my_function():
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"{func.__name__} completed",
            extra={"function": func.__name__, "duration_ms": duration_ms},
        )
        return result

    return wrapper


def chunked(iterable: list, size: int):
    """
    Yield successive chunks of a given size from an iterable.

    Args:
        iterable: List to chunk.
        size: Chunk size.

    Yields:
        List chunks.
    """
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def sanitize_column_name(name: str) -> str:
    """
    Sanitize a column name for SQL compatibility.

    Args:
        name: Raw column name.

    Returns:
        Cleaned, lowercase, underscore-separated column name.
    """
    import re

    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def validate_dataframe(df, expected_columns: list, table_name: str) -> bool:
    """
    Validate that a DataFrame contains expected columns.

    Args:
        df: pandas DataFrame to validate.
        expected_columns: List of required column names.
        table_name: Name of the table (for logging).

    Returns:
        True if valid, raises ValueError if not.
    """
    missing = set(expected_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Table '{table_name}' missing columns: {missing}")
    logger.info(f"Validated {table_name}: {len(df)} rows, {len(df.columns)} columns")
    return True


def validate_not_empty(df, table_name: str) -> bool:
    """
    Validate that a DataFrame is not empty.

    Args:
        df: pandas DataFrame to validate.
        table_name: Name of the table.

    Returns:
        True if not empty, raises ValueError if empty.
    """
    if df is None or len(df) == 0:
        raise ValueError(f"Table '{table_name}' is empty (0 rows)")
    return True
