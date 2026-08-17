"""Small PostgreSQL connection dependency used by API routes."""

from collections.abc import Generator

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from services.api.config import get_settings


def get_connection() -> Generator[Connection[dict[str, object]], None, None]:
    """Yield one request-scoped connection and close it when the request ends."""

    with psycopg.connect(get_settings().database_url, row_factory=dict_row) as connection:
        yield connection


def check_connection(connection: Connection[dict[str, object]]) -> bool:
    """Return whether PostgreSQL responds without exposing connection details."""

    connection.execute("select 1")
    return True
