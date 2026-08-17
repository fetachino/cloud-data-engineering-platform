from __future__ import annotations

import ast
from pathlib import Path

DAG_PATH = Path("airflow/dags/ecommerce_analytics_pipeline.py")


def test_airflow_dag_file_is_parseable_python() -> None:
    ast.parse(DAG_PATH.read_text(encoding="utf-8"))


def test_airflow_dag_declares_expected_tasks_and_dependencies() -> None:
    dag_source = DAG_PATH.read_text(encoding="utf-8")

    for task_id in ["wait_for_postgres", "check_source_data", "dbt_debug", "dbt_run", "dbt_test"]:
        assert f'task_id="{task_id}"' in dag_source

    expected_dependencies = (
        "wait_for_postgres >> check_source_data >> dbt_debug >> dbt_run >> dbt_test"
    )
    assert expected_dependencies in dag_source


def test_airflow_dag_keeps_transformation_logic_in_dbt() -> None:
    dag_source = DAG_PATH.read_text(encoding="utf-8")

    assert "dbt run" in dag_source
    assert "dbt test" in dag_source
    assert "insert into" not in dag_source.lower()
    assert "create table" not in dag_source.lower()


def test_source_readiness_script_checks_processed_events() -> None:
    script = Path("scripts/check_source_readiness.py").read_text(encoding="utf-8")

    assert "processed_events" in script
    assert "SOURCE_MIN_PROCESSED_EVENTS" in script
