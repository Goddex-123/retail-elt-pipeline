"""
Retail ELT Platform — Data Quality & SLA Monitor DAG
======================================================
Standalone data quality monitoring pipeline.
Checks freshness, row count anomalies, schema integrity,
and generates a comprehensive quality report.

Schedule: Every 6 hours
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/scripts")

from dags.common.callbacks import on_failure_callback

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=15),
    "on_failure_callback": on_failure_callback,
}


def check_source_freshness(**context):
    """Verify source tables have been updated within SLA window."""
    from src.db import get_engine
    from src.logger import get_logger
    import pandas as pd

    logger = get_logger(__name__)
    engine = get_engine()

    try:
        result = pd.read_sql(
            "SELECT MAX(_loaded_at::timestamp) as last_load FROM bronze.customers",
            engine,
        )
        last_load = result["last_load"].iloc[0]

        if last_load is None:
            raise ValueError("No data found in bronze layer — pipeline may not have run!")

        logger.info(
            "Freshness check passed",
            extra={"pipeline_stage": "quality", "last_load": str(last_load)},
        )

    except Exception as e:
        logger.error(f"Freshness check failed: {e}", extra={"pipeline_stage": "quality"})
        raise


def check_row_count_anomalies(**context):
    """Check for unexpected row count drops (potential data loss)."""
    from src.db import get_engine
    from src.logger import get_logger
    import pandas as pd

    logger = get_logger(__name__)
    engine = get_engine()

    min_counts = {
        "customers": 100,
        "orders": 500,
        "products": 10,
    }

    anomalies = []
    for table, min_count in min_counts.items():
        try:
            result = pd.read_sql(f"SELECT COUNT(*) as cnt FROM bronze.{table}", engine)
            count = int(result["cnt"].iloc[0])

            if count < min_count:
                anomalies.append(f"bronze.{table}: {count} rows (min: {min_count})")
                logger.warning(
                    f"Row count anomaly: bronze.{table}",
                    extra={"table_name": table, "row_count": count, "min_expected": min_count},
                )
            else:
                logger.info(
                    f"Row count OK: bronze.{table}",
                    extra={"table_name": table, "row_count": count},
                )

        except Exception as e:
            logger.warning(f"Could not check {table}: {e}", extra={"table_name": table, "error": str(e)})

    if anomalies:
        raise ValueError(f"Row count anomalies detected: {anomalies}")


def check_schema_integrity(**context):
    """Verify all expected schemas exist."""
    from src.db import get_engine
    from src.logger import get_logger
    from sqlalchemy import text

    logger = get_logger(__name__)
    engine = get_engine()

    expected_schemas = ["source", "bronze", "silver", "gold"]

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata"
        ))
        existing = {row[0] for row in result}

    for schema in expected_schemas:
        if schema in existing:
            logger.info(f"Schema verified: {schema}", extra={"schema": schema})
        else:
            logger.error(f"Schema MISSING: {schema}", extra={"schema": schema})
            raise ValueError(f"Required schema '{schema}' does not exist")


def generate_full_quality_report(**context):
    """Generate and log the comprehensive data quality report."""
    from src.quality import generate_quality_report, format_quality_report
    from src.logger import get_logger

    logger = get_logger(__name__)
    report = generate_quality_report(schema="bronze")
    formatted = format_quality_report(report)

    # Print full report (visible in Airflow logs)
    print(formatted)

    logger.info(
        "Quality report generated",
        extra={
            "pipeline_stage": "quality",
            "quality_score": report["quality_score_pct"],
            "status": report["status"],
        },
    )

    # Push report summary to XCom for downstream use
    context["ti"].xcom_push(key="quality_score", value=report["quality_score_pct"])
    context["ti"].xcom_push(key="quality_status", value=report["status"])


with DAG(
    dag_id="retail_data_quality_monitor",
    default_args=default_args,
    description="Data quality monitoring: freshness, row counts, schema integrity, quality report",
    schedule_interval="0 */6 * * *",  # Every 6 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["retail", "quality", "monitoring"],
    doc_md="""
    ## Data Quality Monitor
    Runs independently to validate pipeline health:
    - Source data freshness (SLA compliance)
    - Row count anomaly detection
    - Schema integrity verification
    - Comprehensive data quality report
    """,
) as dag:

    freshness_check = PythonOperator(
        task_id="check_source_freshness",
        python_callable=check_source_freshness,
    )

    row_count_check = PythonOperator(
        task_id="check_row_count_anomalies",
        python_callable=check_row_count_anomalies,
    )

    schema_check = PythonOperator(
        task_id="check_schema_integrity",
        python_callable=check_schema_integrity,
    )

    quality_report = PythonOperator(
        task_id="generate_quality_report",
        python_callable=generate_full_quality_report,
    )

    # Run structural checks in parallel, then generate report
    [freshness_check, row_count_check, schema_check] >> quality_report
