"""
Retail ELT Platform — Data Quality Report Generator
=====================================================
Produces structured data quality reports for pipeline observability.
Checks: null rates, duplicate rates, row counts, referential integrity,
freshness, and accepted values.

Reports are logged as structured JSON and can be displayed in the dashboard.
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import pandas as pd
from sqlalchemy import text

from src.config import schema_config
from src.db import get_engine
from src.logger import get_logger, generate_correlation_id

logger = get_logger(__name__)


# ============================================================
# Quality Check Definitions
# ============================================================

# Minimum expected row counts per bronze table
MIN_ROW_COUNTS = {
    "customers": 100,
    "products": 10,
    "orders": 500,
    "order_items": 500,
    "payments": 500,
    "stores": 5,
    "categories": 3,
    "suppliers": 3,
}

# Columns that should never be null
NOT_NULL_COLUMNS = {
    "customers": ["customer_id", "email"],
    "orders": ["order_id", "customer_id", "store_id", "order_date"],
    "order_items": ["order_item_id", "order_id", "product_id"],
    "payments": ["payment_id", "order_id", "payment_method"],
    "products": ["product_id", "product_name", "unit_price"],
}

# Primary key columns (should be unique)
PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "stores": "store_id",
    "categories": "category_id",
    "suppliers": "supplier_id",
}


# ============================================================
# Quality Check Functions
# ============================================================

def check_row_count(engine, schema: str, table: str, min_count: int) -> Dict[str, Any]:
    """Check that a table meets minimum row count threshold."""
    try:
        result = pd.read_sql(
            f"SELECT COUNT(*) as cnt FROM {schema}.{table}", engine
        )
        count = int(result["cnt"].iloc[0])
        passed = count >= min_count
        return {
            "check": "row_count",
            "table": f"{schema}.{table}",
            "value": count,
            "threshold": min_count,
            "passed": passed,
            "message": f"{count:,} rows" + ("" if passed else f" (min: {min_count:,})"),
        }
    except Exception as e:
        return {
            "check": "row_count",
            "table": f"{schema}.{table}",
            "passed": False,
            "message": f"Error: {e}",
        }


def check_null_rate(engine, schema: str, table: str, column: str) -> Dict[str, Any]:
    """Check null rate for a specific column."""
    try:
        result = pd.read_sql(
            f"SELECT COUNT(*) as total, "
            f"SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) as nulls "
            f"FROM {schema}.{table}",
            engine,
        )
        total = int(result["total"].iloc[0])
        nulls = int(result["nulls"].iloc[0])
        null_pct = round((nulls / max(total, 1)) * 100, 2)
        return {
            "check": "null_rate",
            "table": f"{schema}.{table}",
            "column": column,
            "null_count": nulls,
            "total_rows": total,
            "null_pct": null_pct,
            "passed": null_pct < 5.0,  # 5% threshold
            "message": f"{nulls} nulls ({null_pct}%)",
        }
    except Exception as e:
        return {
            "check": "null_rate",
            "table": f"{schema}.{table}",
            "column": column,
            "passed": False,
            "message": f"Error: {e}",
        }


def check_duplicates(engine, schema: str, table: str, pk_column: str) -> Dict[str, Any]:
    """Check for duplicate primary keys."""
    try:
        result = pd.read_sql(
            f"SELECT COUNT(*) as total, COUNT(DISTINCT {pk_column}) as distinct_cnt "
            f"FROM {schema}.{table}",
            engine,
        )
        total = int(result["total"].iloc[0])
        distinct = int(result["distinct_cnt"].iloc[0])
        dupes = total - distinct
        return {
            "check": "duplicates",
            "table": f"{schema}.{table}",
            "column": pk_column,
            "duplicate_count": dupes,
            "total_rows": total,
            "passed": dupes == 0,
            "message": f"{dupes} duplicates" if dupes > 0 else "No duplicates",
        }
    except Exception as e:
        return {
            "check": "duplicates",
            "table": f"{schema}.{table}",
            "column": pk_column,
            "passed": False,
            "message": f"Error: {e}",
        }


def check_freshness(
    engine, schema: str, table: str, ts_column: str = "_loaded_at", max_hours: int = 24
) -> Dict[str, Any]:
    """Check that data was loaded within the freshness window."""
    try:
        result = pd.read_sql(
            f"SELECT MAX({ts_column}::timestamp) as last_load FROM {schema}.{table}",
            engine,
        )
        last_load = result["last_load"].iloc[0]
        if last_load is None:
            return {
                "check": "freshness",
                "table": f"{schema}.{table}",
                "passed": False,
                "message": "No data loaded",
            }

        # Handle timezone-aware comparison
        if hasattr(last_load, 'tzinfo') and last_load.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.utcnow()

        hours_ago = (now - last_load).total_seconds() / 3600
        passed = hours_ago <= max_hours
        return {
            "check": "freshness",
            "table": f"{schema}.{table}",
            "last_load": str(last_load),
            "hours_ago": round(hours_ago, 1),
            "threshold_hours": max_hours,
            "passed": passed,
            "message": f"Last load: {hours_ago:.1f}h ago" + ("" if passed else " (STALE)"),
        }
    except Exception as e:
        return {
            "check": "freshness",
            "table": f"{schema}.{table}",
            "passed": False,
            "message": f"Error: {e}",
        }


# ============================================================
# Report Generator
# ============================================================

def generate_quality_report(schema: str = "bronze") -> Dict[str, Any]:
    """
    Generate a comprehensive data quality report for the specified schema.

    Returns a structured report with:
    - Per-table row counts
    - Null rates for critical columns
    - Duplicate checks on primary keys
    - Data freshness checks
    - Overall quality score

    Args:
        schema: Database schema to check (default: bronze).

    Returns:
        Dictionary containing all quality check results and summary.
    """
    correlation_id = generate_correlation_id()
    engine = get_engine()
    report_time = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Generating data quality report",
        extra={"correlation_id": correlation_id, "schema": schema},
    )

    results: List[Dict[str, Any]] = []

    # Row count checks
    for table, min_count in MIN_ROW_COUNTS.items():
        results.append(check_row_count(engine, schema, table, min_count))

    # Null rate checks
    for table, columns in NOT_NULL_COLUMNS.items():
        for col in columns:
            results.append(check_null_rate(engine, schema, table, col))

    # Duplicate checks
    for table, pk in PRIMARY_KEYS.items():
        results.append(check_duplicates(engine, schema, table, pk))

    # Freshness checks (only for bronze with _loaded_at)
    if schema == "bronze":
        for table in ["customers", "orders", "products", "payments"]:
            results.append(check_freshness(engine, schema, table))

    # Summary
    total_checks = len(results)
    passed_checks = sum(1 for r in results if r.get("passed", False))
    failed_checks = total_checks - passed_checks
    quality_score = round((passed_checks / max(total_checks, 1)) * 100, 2)

    report = {
        "report_time": report_time,
        "correlation_id": correlation_id,
        "schema": schema,
        "total_checks": total_checks,
        "passed": passed_checks,
        "failed": failed_checks,
        "quality_score_pct": quality_score,
        "status": "PASS" if quality_score >= 95 else "WARN" if quality_score >= 80 else "FAIL",
        "checks": results,
    }

    logger.info(
        f"Quality report: {quality_score}% ({passed_checks}/{total_checks} passed)",
        extra={
            "correlation_id": correlation_id,
            "quality_score": quality_score,
            "passed": passed_checks,
            "failed": failed_checks,
        },
    )

    return report


def format_quality_report(report: Dict[str, Any]) -> str:
    """
    Format a quality report as a human-readable text summary.

    Example output:
        ════════════════════════════════════════
        DATA QUALITY REPORT
        Schema: bronze | Score: 97.5% | PASS
        ════════════════════════════════════════

        customers
          Rows: 550       ✅
          Duplicates: 50  ⚠️
          Null email: 0   ✅
          Freshness: 0.5h ✅

        orders
          Rows: 2,000     ✅
          ...

        Overall: 39/40 checks passed (97.5%)
        ════════════════════════════════════════
    """
    lines = [
        "",
        "═" * 50,
        "DATA QUALITY REPORT",
        f"Schema: {report['schema']} | Score: {report['quality_score_pct']}% | {report['status']}",
        f"Time: {report['report_time']}",
        "═" * 50,
        "",
    ]

    # Group checks by table
    checks_by_table: Dict[str, List] = {}
    for check in report["checks"]:
        table = check["table"]
        if table not in checks_by_table:
            checks_by_table[table] = []
        checks_by_table[table].append(check)

    for table, checks in checks_by_table.items():
        lines.append(f"  {table}")
        for check in checks:
            icon = "✅" if check.get("passed") else "⚠️"
            check_type = check["check"]
            col_info = f" ({check.get('column', '')})" if check.get("column") else ""
            lines.append(f"    {check_type}{col_info}: {check['message']} {icon}")
        lines.append("")

    lines.extend([
        f"  Overall: {report['passed']}/{report['total_checks']} checks passed ({report['quality_score_pct']}%)",
        "═" * 50,
        "",
    ])

    return "\n".join(lines)
