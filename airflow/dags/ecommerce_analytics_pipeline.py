from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "${DBT_PROJECT_DIR:-/opt/airflow/analytics}"
DBT_PROFILES_DIR = "${DBT_PROFILES_DIR:-/opt/airflow/analytics/profiles}"


with DAG(
    dag_id="ecommerce_analytics_pipeline",
    description="Build and test dbt analytics marts from the local operational PostgreSQL store.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=10),
    },
    dagrun_timeout=timedelta(minutes=20),
    tags=["analytics", "dbt", "milestone-2"],
) as dag:
    wait_for_postgres = BashOperator(
        task_id="wait_for_postgres",
        bash_command="python /opt/airflow/scripts/wait_for_postgres.py",
        execution_timeout=timedelta(minutes=2),
    )

    check_source_data = BashOperator(
        task_id="check_source_data",
        bash_command="python /opt/airflow/scripts/check_source_readiness.py",
        execution_timeout=timedelta(minutes=2),
    )

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=(
            f"dbt debug --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
        execution_timeout=timedelta(minutes=3),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"dbt test --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
        execution_timeout=timedelta(minutes=10),
    )

    wait_for_postgres >> check_source_data >> dbt_debug >> dbt_run >> dbt_test
