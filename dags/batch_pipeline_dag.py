from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
import os

# Define defaults
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Path configuration
DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DAG_FOLDER)
DBT_DIR = os.path.join(PROJECT_ROOT, 'dbt_project')

# Define DAG
with DAG(
    'batch_event_pipeline',
    default_args=default_args,
    description='End-to-end batch pipeline: Ingest -> Load to BigQuery -> dbt Transform',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Ingest and Clean CSV
    ingest_data_task = BashOperator(
        task_id='ingest_data_task',
        bash_command=f'python {os.path.join(PROJECT_ROOT, "etl", "ingest.py")}',
    )

    # Task 2: Load Cleaned CSV to BigQuery
    load_to_bigquery_task = BashOperator(
        task_id='load_to_bigquery_task',
        bash_command=f'python {os.path.join(PROJECT_ROOT, "etl", "load_to_bq.py")}',
    )

    # Task 3: Run dbt models
    run_dbt_models_task = BashOperator(
        task_id='run_dbt_models_task',
        bash_command=f'cd {DBT_DIR} && dbt run --profiles-dir .',
    )

    # Define Dependencies
    ingest_data_task >> load_to_bigquery_task >> run_dbt_models_task
