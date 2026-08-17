from __future__ import annotations

from pathlib import Path

MIGRATION_PATH = Path("db/migrations/versions/0001_operational_schema.py")


def test_initial_migration_contains_expected_operational_tables() -> None:
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    for table in [
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "inventory",
        "shipments",
        "processed_events",
    ]:
        assert f'"{table}"' in migration


def test_processed_events_has_event_id_primary_key() -> None:
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    assert '"processed_events"' in migration
    assert 'sa.Column("event_id", sa.Uuid(), primary_key=True)' in migration
