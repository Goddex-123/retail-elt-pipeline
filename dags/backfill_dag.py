"""
Retail ELT Platform — Backfill DAG
====================================
Parameterized DAG for historical data backfill.
Manually triggered with date range parameters.

Schedule: None (manual trigger only)
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.param import Param
from datetime import datetime, timedelta
import sys

sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/scripts")

from dags.common.callbacks import on_failure_callback

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
}


def run_backfill_generation(**context):
    """Generate historical data for the specified date range."""
    params = context["params"]
    start_date = params.get("start_date", "2024-01-01")
    end_date = params.get("end_date", "2024-12-31")
    record_count = params.get("record_count", 5000)

    from scripts.data_generator import generate_all_data, load_to_db

    print(f"Backfilling data from {start_date} to {end_date} ({record_count} records)")
    tables = generate_all_data(n_customers=500, n_orders=record_count)
    load_to_db(tables)


def run_backfill_bronze(**context):
    """Load backfill data to bronze."""
    from scripts.bronze_loader import extract_and_load

    extract_and_load(batch_id=f"backfill-{datetime.now().strftime('%Y%m%d%H%M%S')}")


with DAG(
    dag_id="retail_backfill",
    default_args=default_args,
    description="Manual backfill DAG with configurable date range",
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["retail", "backfill", "manual"],
    params={
        "start_date": Param(
            default="2024-01-01",
            type="string",
            description="Backfill start date (YYYY-MM-DD)",
        ),
        "end_date": Param(
            default="2024-12-31",
            type="string",
            description="Backfill end date (YYYY-MM-DD)",
        ),
        "record_count": Param(
            default=5000,
            type="integer",
            description="Number of order records to generate",
        ),
    },
    doc_md="""
    ## Backfill Pipeline
    Manually trigger this DAG to backfill historical data.

    ### Parameters
    - `start_date`: Start of backfill window
    - `end_date`: End of backfill window
    - `record_count`: Number of order records to generate

    ### Usage
    Trigger via Airflow UI with custom parameters.
    """,
) as dag:

    backfill_generate = PythonOperator(
        task_id="generate_backfill_data",
        python_callable=run_backfill_generation,
    )

    backfill_bronze = PythonOperator(
        task_id="load_backfill_bronze",
        python_callable=run_backfill_bronze,
    )

    dbt_full_refresh = BashOperator(
        task_id="dbt_full_refresh",
        bash_command="cd /opt/airflow/dbt_retail && dbt run --full-refresh --profiles-dir .",
    )

    dbt_test_all = BashOperator(
        task_id="dbt_test_all",
        bash_command="cd /opt/airflow/dbt_retail && dbt test --profiles-dir .",
    )

    backfill_generate >> backfill_bronze >> dbt_full_refresh >> dbt_test_all
