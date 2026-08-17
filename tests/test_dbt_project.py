from __future__ import annotations

from pathlib import Path

ANALYTICS_DIR = Path("analytics")


def test_dbt_project_declares_analytics_profile_and_layers() -> None:
    project = (ANALYTICS_DIR / "dbt_project.yml").read_text(encoding="utf-8")

    assert "profile: ecommerce_analytics" in project
    assert "staging:" in project
    assert "intermediate:" in project
    assert "marts:" in project


def test_required_dbt_models_exist() -> None:
    required_models = [
        "models/staging/stg_customers.sql",
        "models/staging/stg_products.sql",
        "models/staging/stg_orders.sql",
        "models/staging/stg_order_items.sql",
        "models/staging/stg_payments.sql",
        "models/staging/stg_inventory.sql",
        "models/staging/stg_shipments.sql",
        "models/marts/dim_customers.sql",
        "models/marts/dim_products.sql",
        "models/marts/fct_orders.sql",
        "models/marts/fct_order_items.sql",
        "models/marts/fct_payments.sql",
    ]

    for model_path in required_models:
        assert (ANALYTICS_DIR / model_path).exists()


def test_dbt_profile_uses_environment_driven_postgres_connection() -> None:
    profile = (ANALYTICS_DIR / "profiles/profiles.yml").read_text(encoding="utf-8")

    for variable in ["DBT_HOST", "DBT_PORT", "DBT_USER", "DBT_PASSWORD", "DBT_DATABASE"]:
        assert f"env_var('{variable}'" in profile
    assert "env_var('DBT_SCHEMA', 'analytics')" in profile


def test_marts_build_from_refs_not_raw_operational_sources() -> None:
    for model_path in (ANALYTICS_DIR / "models/marts").glob("*.sql"):
        sql = model_path.read_text(encoding="utf-8")
        assert "source('operational'" not in sql
        assert "{{ ref(" in sql


def test_dbt_data_quality_tests_cover_business_rules() -> None:
    test_names = {path.name for path in (ANALYTICS_DIR / "tests").glob("*.sql")}

    assert "assert_fct_orders_non_negative.sql" in test_names
    assert "assert_order_item_quantities_positive.sql" in test_names
    assert "assert_payment_amounts_non_negative.sql" in test_names
    assert "assert_delivered_shipments_have_timestamp.sql" in test_names
