# Architecture

## Milestone 1 Scope

Milestone 1 builds the local event pipeline foundation:

```text
services/producer -> Kafka -> services/consumer -> PostgreSQL
```

## Service Boundaries

- `shared/`: event contracts, configuration, and logging helpers
- `services/producer/`: deterministic synthetic event generation and Kafka publishing
- `services/consumer/`: Kafka consumption, validation, idempotency, and persistence
- `db/migrations/`: Alembic-managed operational schema
- `docs/`: event contract documentation
- `tests/`: focused unit tests

## Kafka Design

Topic: `ecommerce.events.v1`

Milestone 1 uses one topic and one local partition. Related order lifecycle events share a `correlation_id`, which is also used as the Kafka message key. This is a practical local choice for preserving ordering where possible without pretending to solve distributed ordering generally.

## Database Design

Operational PostgreSQL tables:

- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `inventory`
- `shipments`
- `processed_events`

Domain tables store typed columns rather than opaque event JSON. `processed_events` is the idempotency ledger.

## Failure Handling

- Malformed events are rejected and logged without crashing the consumer.
- Duplicate `event_id`s are ignored after the first successful processing attempt.
- Database failures bubble out of the repository, are logged, and prevent offset commit.
- The system uses at-least-once delivery semantics with idempotent processing where practical.
