from __future__ import annotations

import os

import psycopg

REQUIRED_TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "inventory",
    "shipments",
    "processed_events",
]


def database_url() -> str:
    return os.getenv(
        "ANALYTICS_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql://platform:platform@localhost:5432/ecommerce"),
    )


def main() -> None:
    minimum_events = int(os.getenv("SOURCE_MIN_PROCESSED_EVENTS", "1"))

    with (
        psycopg.connect(database_url(), connect_timeout=5) as connection,
        connection.cursor() as cursor,
    ):
        for table_name in REQUIRED_TABLES:
            cursor.execute("select to_regclass(%s)", (table_name,))
            if cursor.fetchone()[0] is None:
                raise RuntimeError(f"Required operational table is missing: {table_name}")

        cursor.execute("select count(*) from processed_events")
        processed_events = cursor.fetchone()[0]
        if processed_events < minimum_events:
            raise RuntimeError(
                "Operational source data is not ready: "
                f"processed_events={processed_events}, minimum={minimum_events}"
            )


if __name__ == "__main__":
    main()
