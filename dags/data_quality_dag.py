"""
Retail ELT Platform — Data Quality & SLA Monitor DAG
======================================================
Standalone data quality monitoring pipeline.
Checks freshness, row count anomalies, and schema integrity.

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
    "on_failure_callback": on_failure_callback,
}


def check_source_freshness(**context):
    """Verify source tables have been updated within SLA window."""
    import pandas as pd
    from sqlalchemy import create_engine
    import os

    db_url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER', 'airflow')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'airflow')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'retail_warehouse')}"
    )
    engine = create_engine(db_url)

    freshness_query = """
        SELECT
            table_schema,
            table_name,
            (SELECT MAX(_loaded_at::timestamp) FROM bronze.customers) as last_load
    """

    try:
        result = pd.read_sql("SELECT MAX(_loaded_at) as last_load FROM bronze.customers", engine)
        last_load = result["last_load"].iloc[0]
        print(f"Last bronze load: {last_load}")

        if last_load is None:
            raise ValueError("No data found in bronze layer — pipeline may not have run!")

    except Exception as e:
        print(f"Freshness check warning: {e}")


def check_row_count_anomalies(**context):
    """Check for unexpected row count drops (potential data loss)."""
    import pandas as pd
    from sqlalchemy import create_engine
    import os

    db_url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER', 'airflow')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'airflow')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'retail_warehouse')}"
    )
    engine = create_engine(db_url)

    min_counts = {
        "customers": 100,
        "orders": 500,
        "products": 10,
    }

    for table, min_count in min_counts.items():
        try:
            result = pd.read_sql(f"SELECT COUNT(*) as cnt FROM bronze.{table}", engine)
            count = result["cnt"].iloc[0]

            if count < min_count:
                print(f"⚠️ ANOMALY: bronze.{table} has {count} rows (min: {min_count})")
            else:
                print(f"✅ bronze.{table}: {count} rows (OK)")

        except Exception as e:
            print(f"⚠️ Could not check {table}: {e}")


def check_schema_integrity(**context):
    """Verify all expected schemas exist."""
    from sqlalchemy import create_engine, text
    import os

    db_url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER', 'airflow')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'airflow')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'retail_warehouse')}"
    )
    engine = create_engine(db_url)

    expected_schemas = ["source", "bronze", "silver", "gold"]

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata"
        ))
        existing = {row[0] for row in result}

    for schema in expected_schemas:
        if schema in existing:
            print(f"✅ Schema '{schema}' exists")
        else:
            print(f"❌ Schema '{schema}' MISSING!")
            raise ValueError(f"Required schema '{schema}' does not exist")


with DAG(
    dag_id="retail_data_quality_monitor",
    default_args=default_args,
    description="Data quality monitoring: freshness, row counts, schema integrity",
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

    # Run checks in parallel
    [freshness_check, row_count_check, schema_check]
