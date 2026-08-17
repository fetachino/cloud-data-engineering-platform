from __future__ import annotations

from dataclasses import dataclass

from services.consumer.processor import EventProcessor
from services.consumer.repository import ProcessResult
from services.producer.generator import GeneratorConfig, generate_events
from shared.events.models import EcommerceEvent


@dataclass
class FakeRepository:
    result: ProcessResult
    calls: int = 0

    def process_event(self, event: EcommerceEvent) -> ProcessResult:
        self.calls += 1
        return self.result


class FailingRepository:
    def process_event(self, event: EcommerceEvent) -> ProcessResult:
        raise RuntimeError("database unavailable")


def test_processor_acknowledges_malformed_event_without_repository_call() -> None:
    repository = FakeRepository(ProcessResult(processed=True, reason="processed"))
    processor = EventProcessor(repository)  # type: ignore[arg-type]

    result = processor.process_message(b'{"event_type":"customer_created"}')

    assert result.acknowledged is True
    assert result.reason == "invalid_event"
    assert repository.calls == 0


def test_processor_acknowledges_duplicate_event() -> None:
    repository = FakeRepository(ProcessResult(processed=False, reason="duplicate_event"))
    processor = EventProcessor(repository)  # type: ignore[arg-type]
    event = generate_events(GeneratorConfig(event_count=1))[0]

    result = processor.process_message(event.model_dump_json())

    assert result.acknowledged is True
    assert result.reason == "duplicate_event"
    assert repository.calls == 1


def test_processor_does_not_acknowledge_database_failure() -> None:
    processor = EventProcessor(FailingRepository())  # type: ignore[arg-type]
    event = generate_events(GeneratorConfig(event_count=1))[0]

    result = processor.process_message(event.model_dump_json())

    assert result.acknowledged is False
    assert result.reason == "processing_failed"
