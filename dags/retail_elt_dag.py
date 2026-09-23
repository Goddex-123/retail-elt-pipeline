"""
Retail ELT Platform — Daily Pipeline DAG
==========================================
Full daily ELT pipeline: Generate → Bronze → dbt Staging →
dbt Test → dbt Marts → dbt Snapshot → Quality Report

Schedule: Daily at 02:00 UTC
SLA: Must complete by 06:00 UTC
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import sys
import os

# Ensure project modules are importable
sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/scripts")

from dags.common.callbacks import on_failure_callback, on_success_callback, sla_miss_callback

# ============================================================
# DAG Configuration
# ============================================================

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
    "execution_timeout": timedelta(minutes=30),
    "on_failure_callback": on_failure_callback,
    "sla": timedelta(hours=4),
}


# ============================================================
# Python Callables
# ============================================================

def run_data_generation(**context):
    """Generate synthetic source data for all 13 tables."""
    from scripts.data_generator import generate_all_data, load_to_db
    from src.logger import get_logger

    logger = get_logger(__name__)
    tables = generate_all_data(n_customers=500, n_orders=2000)

    total_rows = sum(len(df) for df in tables.values())
    logger.info(
        "Data generation complete",
        extra={
            "pipeline_stage": "ingestion",
            "tables_generated": len(tables),
            "rows_processed": total_rows,
        },
    )

    load_to_db(tables)
    context["ti"].xcom_push(key="tables_generated", value=list(tables.keys()))
    context["ti"].xcom_push(key="total_rows_generated", value=total_rows)


def run_bronze_load(**context):
    """Extract from source and load into bronze schema."""
    from scripts.bronze_loader import extract_and_load
    from src.logger import get_logger

    logger = get_logger(__name__)
    stats = extract_and_load()

    success_count = sum(1 for v in stats.values() if v.get("status") == "success")
    total_rows = sum(v.get("rows", 0) for v in stats.values())
    logger.info(
        "Bronze load complete",
        extra={
            "pipeline_stage": "bronze_load",
            "tables_loaded": success_count,
            "rows_processed": total_rows,
        },
    )

    context["ti"].xcom_push(key="bronze_stats", value=str(stats))


def run_quality_report(**context):
    """Generate and log a data quality report after the pipeline completes."""
    from src.quality import generate_quality_report, format_quality_report
    from src.logger import get_logger

    logger = get_logger(__name__)
    report = generate_quality_report(schema="bronze")
    formatted = format_quality_report(report)

    # Print the formatted report (visible in Airflow task logs)
    print(formatted)

    logger.info(
        "Data quality report generated",
        extra={
            "pipeline_stage": "quality",
            "quality_score": report["quality_score_pct"],
            "checks_passed": report["passed"],
            "checks_failed": report["failed"],
            "status": report["status"],
        },
    )

    if report["status"] == "FAIL":
        raise ValueError(
            f"Data quality below threshold: {report['quality_score_pct']}% "
            f"({report['failed']} checks failed)"
        )


# ============================================================
# DAG Definition
# ============================================================

with DAG(
    dag_id="retail_daily_pipeline",
    default_args=default_args,
    description="Full daily ELT pipeline: Source → Bronze → Silver → Gold",
    schedule_interval="0 2 * * *",  # Daily at 02:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["retail", "elt", "daily", "production"],
    on_success_callback=on_success_callback,
    sla_miss_callback=sla_miss_callback,
    doc_md="""
    ## Retail Daily Pipeline
    **Owner:** Data Engineering Team
    **Schedule:** Daily at 02:00 UTC
    **SLA:** 4 hours

    ### Pipeline Flow
    1. Generate synthetic source data (13 tables)
    2. Load raw data into Bronze schema
    3. dbt staging models (Bronze → Silver)
    4. dbt data quality tests
    5. dbt mart models (Silver → Gold)
    6. dbt SCD2 customer snapshot
    7. Data quality report
    """,
) as dag:

    # ---- Task Group: Ingestion ----
    with TaskGroup(group_id="ingestion") as ingestion_group:
        generate_data = PythonOperator(
            task_id="generate_source_data",
            python_callable=run_data_generation,
            doc_md="Generate 13 source tables with Faker",
        )

        load_bronze = PythonOperator(
            task_id="load_bronze_layer",
            python_callable=run_bronze_load,
            doc_md="Extract source → Load bronze with metadata columns",
        )

        generate_data >> load_bronze

    # ---- Task Group: Transformation ----
    with TaskGroup(group_id="transformation") as transform_group:
        dbt_staging = BashOperator(
            task_id="dbt_run_staging",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select staging --profiles-dir .",
            doc_md="Run all 13 staging models (Bronze → Silver)",
        )

        dbt_test_staging = BashOperator(
            task_id="dbt_test_staging",
            bash_command="cd /opt/airflow/dbt_retail && dbt test --select staging --profiles-dir .",
            doc_md="Run data quality tests on staging models",
        )

        dbt_intermediate = BashOperator(
            task_id="dbt_run_intermediate",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select intermediate --profiles-dir .",
            doc_md="Run intermediate enrichment models",
        )

        dbt_staging >> dbt_test_staging >> dbt_intermediate

    # ---- Task Group: Marts ----
    with TaskGroup(group_id="marts") as marts_group:
        dbt_sales_mart = BashOperator(
            task_id="dbt_run_sales_mart",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select marts.sales --profiles-dir .",
        )

        dbt_customer_mart = BashOperator(
            task_id="dbt_run_customer_mart",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select marts.customers --profiles-dir .",
        )

        dbt_inventory_mart = BashOperator(
            task_id="dbt_run_inventory_mart",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select marts.inventory --profiles-dir .",
        )

        dbt_finance_mart = BashOperator(
            task_id="dbt_run_finance_mart",
            bash_command="cd /opt/airflow/dbt_retail && dbt run --select marts.finance --profiles-dir .",
        )

        # Sales mart first (others may depend on fct_orders)
        dbt_sales_mart >> [dbt_customer_mart, dbt_inventory_mart, dbt_finance_mart]

    # ---- dbt Snapshot (SCD2) ----
    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot_customers",
        bash_command="cd /opt/airflow/dbt_retail && dbt snapshot --profiles-dir .",
        doc_md="Run SCD Type 2 snapshot for customer dimension",
    )

    # ---- dbt Test Marts ----
    dbt_test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command="cd /opt/airflow/dbt_retail && dbt test --select marts --profiles-dir .",
        doc_md="Run data quality tests on all mart models",
    )

    # ---- Quality Report ----
    quality_report = PythonOperator(
        task_id="generate_quality_report",
        python_callable=run_quality_report,
        doc_md="Generate data quality report and fail pipeline if score is below threshold",
    )

    # ---- Pipeline Flow ----
    ingestion_group >> transform_group >> marts_group >> dbt_snapshot >> dbt_test_marts >> quality_report
