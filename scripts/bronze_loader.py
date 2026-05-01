"""
Retail ELT Platform — Bronze Layer Loader
==========================================
Extracts data from source schema and loads into bronze schema
with metadata columns for lineage tracking. Implements idempotent
truncate-and-load pattern with transaction safety.

This simulates what tools like Airbyte/Fivetran do in production.
"""

import sys
import os
from datetime import datetime, timezone

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import db_config, schema_config, SOURCE_TABLES
from src.logger import get_logger, generate_correlation_id
from src.db import get_engine, ensure_schemas, get_connection
from src.utils import timer

logger = get_logger(__name__)


@timer
def extract_and_load(
    tables: list = None,
    batch_id: str = None,
) -> dict:
    """
    Extract from source schema and load raw data into bronze schema.
    Adds metadata columns for data lineage:
        - _loaded_at: UTC timestamp of when the record was loaded
        - _source: Origin schema/table identifier
        - _batch_id: Unique ID for this load batch

    Args:
        tables: List of table names to extract. Defaults to all SOURCE_TABLES.
        batch_id: Unique batch identifier. Auto-generated if not provided.

    Returns:
        Dictionary with load statistics per table.
    """
    if tables is None:
        tables = SOURCE_TABLES

    if batch_id is None:
        batch_id = generate_correlation_id()

    engine = get_engine()
    ensure_schemas()

    load_stats = {}
    loaded_at = datetime.now(timezone.utc).isoformat()

    logger.info(
        f"Starting bronze load for {len(tables)} tables",
        extra={"batch_id": batch_id, "pipeline_stage": "bronze_load"},
    )

    for table_name in tables:
        try:
            logger.info(f"Extracting {table_name} from {schema_config.source}...")

            # Extract from source
            df = pd.read_sql(
                f"SELECT * FROM {schema_config.source}.{table_name}",
                engine,
            )

            if df.empty:
                logger.warning(f"No data found in {schema_config.source}.{table_name}")
                load_stats[table_name] = {"status": "empty", "rows": 0}
                continue

            # Add metadata columns for lineage
            df["_loaded_at"] = loaded_at
            df["_source"] = f"{schema_config.source}.{table_name}"
            df["_batch_id"] = batch_id

            # Load to bronze (idempotent: replace entire table)
            df.to_sql(
                table_name,
                engine,
                schema=schema_config.bronze,
                if_exists="replace",
                index=False,
                method="multi",
            )

            load_stats[table_name] = {"status": "success", "rows": len(df)}
            logger.info(
                f"Loaded {table_name} to bronze",
                extra={
                    "table_name": table_name,
                    "row_count": len(df),
                    "batch_id": batch_id,
                    "pipeline_stage": "bronze_load",
                },
            )

        except Exception as e:
            load_stats[table_name] = {"status": "failed", "error": str(e)}
            logger.error(
                f"Failed to load {table_name}: {e}",
                extra={"table_name": table_name, "batch_id": batch_id},
                exc_info=True,
            )
            raise

    # Log summary
    success_count = sum(1 for v in load_stats.values() if v["status"] == "success")
    total_rows = sum(v.get("rows", 0) for v in load_stats.values())

    logger.info(
        f"Bronze load complete: {success_count}/{len(tables)} tables, {total_rows:,} total rows",
        extra={"batch_id": batch_id, "pipeline_stage": "bronze_load"},
    )

    return load_stats


if __name__ == "__main__":
    stats = extract_and_load()
    print("\n✅ Bronze layer load complete!")
    for table, info in stats.items():
        status_icon = "✓" if info["status"] == "success" else "✗"
        print(f"   {status_icon} {table:20s} → {info.get('rows', 0):>6,} rows")
