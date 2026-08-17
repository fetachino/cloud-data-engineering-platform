from __future__ import annotations

import os
import time

import psycopg


def database_url() -> str:
    return os.getenv(
        "ANALYTICS_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql://platform:platform@localhost:5432/ecommerce"),
    )


def main() -> None:
    deadline = time.monotonic() + int(os.getenv("POSTGRES_WAIT_TIMEOUT_SECONDS", "60"))
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            with psycopg.connect(database_url(), connect_timeout=5) as connection:
                connection.execute("select 1")
                return
        except psycopg.Error as exc:
            last_error = exc
            time.sleep(2)

    raise TimeoutError(f"PostgreSQL did not become available: {last_error}")


if __name__ == "__main__":
    main()
