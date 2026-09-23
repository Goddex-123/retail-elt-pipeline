"""
Retail ELT Platform — Structured Logging
=========================================
JSON-formatted structured logs with correlation IDs
for pipeline run tracing and observability.

Uses LoggerAdapter (not setLogRecordFactory) to avoid
global side-effects when setting correlation IDs.
"""

import logging
import json
import uuid
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """Outputs log records as structured JSON for easy parsing by log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach extra fields if present
        for attr in (
            "correlation_id", "run_id", "pipeline_name", "pipeline_stage",
            "table_name", "row_count", "duration_ms", "batch_id",
            "task_name", "rows_processed", "rows_rejected", "status",
            "high_water_mark", "error",
        ):
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class CorrelatedLogger(logging.LoggerAdapter):
    """
    Logger adapter that injects a correlation_id into every log record.

    Unlike setLogRecordFactory, this approach is scoped to a specific
    logger instance and does not affect other loggers in the application.
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        extra = kwargs.get("extra", {})
        extra["correlation_id"] = self.extra.get("correlation_id", "")
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(
    name: str,
    level: str = "INFO",
    correlation_id: Optional[str] = None,
) -> logging.Logger:
    """
    Create a structured logger with optional correlation ID.

    Args:
        name: Logger name (typically __name__).
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        correlation_id: Optional ID to trace a pipeline run across stages.

    Returns:
        Configured logger instance (or CorrelatedLogger adapter).
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if correlation_id:
        return CorrelatedLogger(logger, {"correlation_id": correlation_id})

    return logger


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for a pipeline run."""
    return f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
