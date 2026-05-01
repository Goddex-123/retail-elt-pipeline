"""
Retail ELT Platform — Hourly Incremental Sales DAG
====================================================
Incrementally loads new orders/payments using high-water mark
pattern, then refreshes the sales mart.

Schedule: Every hour
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/scripts")

from dags.common.callbacks import on_failure_callback

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": on_failure_callback,
}


def run_incremental_load(**context):
    """Run incremental extraction using high-water mark."""
    from scripts.incremental_loader import incremental_load

    stats = incremental_load()
    total_rows = sum(v.get("rows", 0) for v in stats.values())
    context["ti"].xcom_push(key="incremental_rows", value=total_rows)


with DAG(
    dag_id="retail_incremental_sales",
    default_args=default_args,
    description="Hourly incremental load for orders, payments, reviews",
    schedule_interval="0 * * * *",  # Every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["retail", "incremental", "hourly"],
    doc_md="""
    ## Incremental Sales Pipeline
    Loads only new records since last run using high-water mark pattern.
    Refreshes the sales mart incrementally.
    """,
) as dag:

    incremental_extract = PythonOperator(
        task_id="incremental_bronze_load",
        python_callable=run_incremental_load,
    )

    dbt_staging_incremental = BashOperator(
        task_id="dbt_run_staging_incremental",
        bash_command="cd /opt/airflow/dbt_retail && dbt run --select stg_orders stg_payments stg_reviews --profiles-dir .",
    )

    dbt_refresh_sales_mart = BashOperator(
        task_id="dbt_refresh_sales_mart",
        bash_command="cd /opt/airflow/dbt_retail && dbt run --select fct_orders daily_sales --profiles-dir .",
    )

    incremental_extract >> dbt_staging_incremental >> dbt_refresh_sales_mart
