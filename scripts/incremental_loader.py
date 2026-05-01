"""
Retail ELT Platform — Incremental Loader
==========================================
Implements high-water mark pattern for incremental loading
of transactional tables (orders, payments, order_items).
Simulates CDC (Change Data Capture) behavior.
"""

import sys
import os
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import schema_config
from src.logger import get_logger, generate_correlation_id
from src.db import get_engine, get_connection
from src.utils import timer

logger = get_logger(__name__)

# Tables eligible for incremental loading and their timestamp columns
INCREMENTAL_TABLES = {
    "orders": "order_date",
    "payments": "payment_date",
    "reviews": "review_date",
}


def get_high_water_mark(engine, table_name: str, ts_column: str) -> str:
    """
    Get the maximum timestamp from the bronze table (high-water mark).

    Args:
        engine: SQLAlchemy engine.
        table_name: Target table name.
        ts_column: Timestamp column to check.

    Returns:
        ISO-formatted timestamp string, or epoch if table doesn't exist.
    """
    try:
        result = pd.read_sql(
            f"SELECT MAX({ts_column}) as hwm FROM {schema_config.bronze}.{table_name}",
            engine,
        )
        hwm = result["hwm"].iloc[0]
        if hwm is not None:
            return str(hwm)
    except Exception:
        pass

    return "1970-01-01 00:00:00"


@timer
def incremental_load(tables: dict = None, batch_id: str = None) -> dict:
    """
    Incrementally load new/changed records from source to bronze
    using high-water mark pattern.

    Args:
        tables: Dict of {table_name: timestamp_column}. Defaults to INCREMENTAL_TABLES.
        batch_id: Unique batch identifier.

    Returns:
        Load statistics per table.
    """
    if tables is None:
        tables = INCREMENTAL_TABLES

    if batch_id is None:
        batch_id = generate_correlation_id()

    engine = get_engine()
    load_stats = {}
    loaded_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        f"Starting incremental load for {len(tables)} tables",
        extra={"batch_id": batch_id, "pipeline_stage": "incremental_load"},
    )

    for table_name, ts_column in tables.items():
        try:
            hwm = get_high_water_mark(engine, table_name, ts_column)
            logger.info(f"High-water mark for {table_name}: {hwm}")

            # Extract only new records since last load
            query = f"""
                SELECT *
                FROM {schema_config.source}.{table_name}
                WHERE {ts_column} > '{hwm}'
                ORDER BY {ts_column}
            """
            df = pd.read_sql(query, engine)

            if df.empty:
                logger.info(f"No new records for {table_name} since {hwm}")
                load_stats[table_name] = {"status": "no_new_data", "rows": 0}
                continue

            # Add metadata
            df["_loaded_at"] = loaded_at
            df["_source"] = f"{schema_config.source}.{table_name}"
            df["_batch_id"] = batch_id
            df["_is_incremental"] = True

            # Append to bronze (not replace — incremental!)
            df.to_sql(
                table_name,
                engine,
                schema=schema_config.bronze,
                if_exists="append",
                index=False,
                method="multi",
            )

            load_stats[table_name] = {"status": "success", "rows": len(df)}
            logger.info(
                f"Incrementally loaded {len(df)} new rows to bronze.{table_name}",
                extra={
                    "table_name": table_name,
                    "row_count": len(df),
                    "batch_id": batch_id,
                    "high_water_mark": hwm,
                },
            )

        except Exception as e:
            load_stats[table_name] = {"status": "failed", "error": str(e)}
            logger.error(f"Incremental load failed for {table_name}: {e}", exc_info=True)

    return load_stats


if __name__ == "__main__":
    stats = incremental_load()
    print("\n✅ Incremental load complete!")
    for table, info in stats.items():
        print(f"   {table:20s} → {info.get('rows', 0):>6,} new rows ({info['status']})")
