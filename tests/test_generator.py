from __future__ import annotations

from services.producer.generator import GeneratorConfig, generate_events
from shared.events import EventType


def test_generation_is_deterministic_for_same_seed() -> None:
    first = generate_events(GeneratorConfig(seed=123, event_count=12))
    second = generate_events(GeneratorConfig(seed=123, event_count=12))

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


def test_generation_honors_event_count() -> None:
    events = generate_events(GeneratorConfig(seed=123, event_count=9))

    assert len(events) == 9


def test_related_order_events_share_correlation_id() -> None:
    events = generate_events(GeneratorConfig(seed=123, event_count=14))
    order_events = [
        event
        for event in events
        if event.event_type
        in {
            EventType.ORDER_CREATED,
            EventType.ORDER_ITEM_ADDED,
            EventType.INVENTORY_ADJUSTED,
            EventType.PAYMENT_COMPLETED,
            EventType.PAYMENT_FAILED,
            EventType.SHIPMENT_CREATED,
            EventType.SHIPMENT_DELIVERED,
        }
    ]

    assert order_events
    assert len({event.correlation_id for event in order_events[:4]}) == 1
