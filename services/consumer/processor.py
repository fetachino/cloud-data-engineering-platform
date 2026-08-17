from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from psycopg import Error as PsycopgError
from pydantic import ValidationError

from services.consumer.repository import EventRepository, ProcessResult
from services.observability.metrics import (
    CONSUMER_DATABASE_FAILURES,
    CONSUMER_EVENTS_PROCESSED,
    CONSUMER_EVENTS_RECEIVED,
    CONSUMER_MALFORMED_EVENTS,
    CONSUMER_PROCESSING_DURATION,
    CONSUMER_PROCESSING_FAILURES,
)
from shared.events import validate_event
from shared.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class MessageResult:
    acknowledged: bool
    reason: str


class EventProcessor:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def process_message(self, raw_value: bytes | str) -> MessageResult:
        CONSUMER_EVENTS_RECEIVED.inc()
        started = perf_counter()
        try:
            event = validate_event(raw_value)
        except (UnicodeDecodeError, ValidationError, ValueError) as exc:
            CONSUMER_MALFORMED_EVENTS.inc()
            CONSUMER_EVENTS_PROCESSED.labels(result="malformed").inc()
            logger.warning("invalid_event_rejected", error_type=type(exc).__name__)
            CONSUMER_PROCESSING_DURATION.observe(perf_counter() - started)
            return MessageResult(acknowledged=True, reason="invalid_event")

        try:
            result: ProcessResult = self.repository.process_event(event)
        except PsycopgError as exc:
            CONSUMER_DATABASE_FAILURES.inc()
            CONSUMER_PROCESSING_FAILURES.inc()
            logger.exception(
                "event_processing_failed",
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                event_type=event.event_type.value,
                error_type=type(exc).__name__,
            )
            CONSUMER_PROCESSING_DURATION.observe(perf_counter() - started)
            return MessageResult(acknowledged=False, reason="processing_failed")
        except Exception:
            CONSUMER_PROCESSING_FAILURES.inc()
            logger.exception(
                "event_processing_failed",
                event_id=str(event.event_id),
                correlation_id=str(event.correlation_id),
                event_type=event.event_type.value,
                error_type="unexpected_error",
            )
            CONSUMER_PROCESSING_DURATION.observe(perf_counter() - started)
            return MessageResult(acknowledged=False, reason="processing_failed")

        result_label = "duplicate" if not result.processed else "processed"
        CONSUMER_EVENTS_PROCESSED.labels(result=result_label).inc()
        logger.info(
            "event_processed",
            event_id=str(event.event_id),
            correlation_id=str(event.correlation_id),
            event_type=event.event_type.value,
            processed=result.processed,
            reason=result.reason,
        )
        CONSUMER_PROCESSING_DURATION.observe(perf_counter() - started)
        return MessageResult(acknowledged=True, reason=result.reason)
