# Event Contracts

Milestone 1 uses a single Kafka topic, `ecommerce.events.v1`, with a typed event envelope and versioned payloads.

## Envelope

Every event contains:

- `event_id`: durable UUID for idempotent processing
- `event_type`: one of the supported e-commerce event names
- `event_version`: currently `1`
- `occurred_at`: timezone-aware ISO-8601 timestamp
- `producer`: logical producer name
- `correlation_id`: UUID shared across related order lifecycle events
- `payload`: event-specific typed object

## Event Types

- `customer_created`
- `product_created`
- `order_created`
- `order_item_added`
- `payment_completed`
- `payment_failed`
- `inventory_adjusted`
- `shipment_created`
- `shipment_delivered`

The Python source of truth is [shared/events/models.py](../shared/events/models.py).
