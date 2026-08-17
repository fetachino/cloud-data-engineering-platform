from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from services.consumer.repository import EventRepository, ProcessResult
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
        try:
            event = validate_event(raw_value)
        except (UnicodeDecodeError, ValidationError, ValueError) as exc:
            logger.warning("invalid_event_rejected", error=str(exc))
            return MessageResult(acknowledged=True, reason="invalid_event")

        try:
            result: ProcessResult = self.repository.process_event(event)
        except Exception:
            logger.exception("event_processing_failed", event_id=str(event.event_id))
            return MessageResult(acknowledged=False, reason="processing_failed")

        logger.info(
            "event_processed",
            event_id=str(event.event_id),
            event_type=event.event_type.value,
            processed=result.processed,
            reason=result.reason,
        )
        return MessageResult(acknowledged=True, reason=result.reason)
