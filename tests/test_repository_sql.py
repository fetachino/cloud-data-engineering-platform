from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from services.consumer.repository import EventRepository
from services.producer.generator import GeneratorConfig, generate_events


class FakeCursor:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row

    def fetchone(self) -> dict[str, object] | None:
        return self.row


class FakeTransaction:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


@dataclass
class FakeConnection:
    claim_duplicate: bool = False
    statements: list[str] = field(default_factory=list)

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def transaction(self) -> FakeTransaction:
        return FakeTransaction()

    def execute(self, query: str, params: tuple[Any, ...]) -> FakeCursor:
        self.statements.append(" ".join(query.split()))
        if "INSERT INTO processed_events" in query:
            return FakeCursor(None if self.claim_duplicate else {"event_id": params[0]})
        return FakeCursor({"ok": True})


def test_duplicate_event_short_circuits_domain_write() -> None:
    connection = FakeConnection(claim_duplicate=True)
    repository = EventRepository(lambda: connection)  # type: ignore[arg-type]
    event = generate_events(GeneratorConfig(event_count=1))[0]

    result = repository.process_event(event)

    assert result.processed is False
    assert result.reason == "duplicate_event"
    assert len(connection.statements) == 1
    assert "INSERT INTO processed_events" in connection.statements[0]


def test_customer_created_maps_to_customers_table() -> None:
    connection = FakeConnection()
    repository = EventRepository(lambda: connection)  # type: ignore[arg-type]
    event = generate_events(GeneratorConfig(event_count=1))[0]

    result = repository.process_event(event)

    assert result.processed is True
    assert any("INSERT INTO customers" in statement for statement in connection.statements)
