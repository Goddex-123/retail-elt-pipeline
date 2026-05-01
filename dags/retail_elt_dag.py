from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure our local scripts are in path (since we mapped the scripts dir to /opt/airflow/scripts)
sys.path.append('/opt/airflow/scripts')

from data_generator import load_to_db as generate_source_data
from custom_extractor import extract_and_load as extract_load_bronze

default_args = {
    'owner': 'soham',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'retail_elt_pipeline',
    default_args=default_args,
    description='A complete ELT pipeline for Bombay Bazaar',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['elt', 'retail', 'learning'],
) as dag:

    # Task 1: Generate Source Data (Simulates an application backend)
    t1_generate_data = PythonOperator(
        task_id='generate_source_data',
        python_callable=generate_source_data,
    )

    # Task 2: Extract from Source and Load to Bronze (Simulates Airbyte)
    t2_extract_load = PythonOperator(
        task_id='extract_and_load_bronze',
        python_callable=extract_load_bronze,
    )

    # Task 3: dbt run staging models (Bronze -> Silver)
    # We use BashOperator to run dbt CLI commands
    t3_dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command='cd /opt/airflow/dbt_retail && dbt run --select staging --profiles-dir .',
    )

    # Task 4: dbt test staging (Data Quality checks!)
    t4_dbt_test = BashOperator(
        task_id='dbt_test_staging',
        bash_command='cd /opt/airflow/dbt_retail && dbt test --select staging --profiles-dir .',
    )

    t5_dbt_marts = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/airflow/dbt_retail && dbt run --select marts --profiles-dir .',
    )

    # Define Dependencies
    t1_generate_data >> t2_extract_load >> t3_dbt_staging >> t4_dbt_test >> t5_dbt_marts
