from __future__ import annotations

from pydantic import ValidationError

from services.producer.generator import GeneratorConfig, generate_events
from shared.events import EventType, validate_event


def test_valid_generated_event_round_trips_through_json_validation() -> None:
    event = generate_events(GeneratorConfig(seed=7, event_count=1))[0]

    validated = validate_event(event.model_dump_json())

    assert validated.event_id == event.event_id
    assert validated.event_type == EventType.CUSTOMER_CREATED
    assert validated.event_version == 1


def test_payload_must_match_event_type() -> None:
    event = generate_events(GeneratorConfig(seed=7, event_count=2))[0].model_dump(mode="json")
    event["event_type"] = "product_created"

    try:
        validate_event(event)
    except ValidationError as exc:
        assert "payload does not match event_type" in str(exc)
    else:
        raise AssertionError("mismatched payload should fail validation")


def test_malformed_event_is_rejected() -> None:
    event = generate_events(GeneratorConfig(seed=7, event_count=1))[0].model_dump(mode="json")
    del event["event_id"]

    try:
        validate_event(event)
    except ValidationError as exc:
        assert "event_id" in str(exc)
    else:
        raise AssertionError("missing event_id should fail validation")
