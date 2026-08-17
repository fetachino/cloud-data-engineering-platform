# Architecture

## Current Scope

The project currently includes the Milestone 1 local event pipeline and the Milestone 2 analytics transformation layer:

```text
services/producer
  -> Kafka
  -> services/consumer
  -> PostgreSQL operational tables
  -> Airflow
  -> dbt staging/intermediate models
  -> dbt dimensional marts in the analytics schema
```

## Service Boundaries

- `shared/`: event contracts, configuration, and logging helpers
- `services/producer/`: deterministic synthetic event generation and Kafka publishing
- `services/consumer/`: Kafka consumption, validation, idempotency, and persistence
- `db/migrations/`: Alembic-managed operational schema
- `analytics/`: dbt project for staging, intermediate, and mart models
- `airflow/dags/`: orchestration for the local analytics transformation workflow
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

## Analytics Warehouse Design

dbt reads the operational tables as sources and writes analytics-ready models into the dedicated `analytics` schema.

- Staging models standardize names and preserve source grain.
- Intermediate models contain reusable order item and payment rollups.
- Mart models expose `dim_customers`, `dim_products`, `fct_orders`, `fct_order_items`, and `fct_payments`.

Operational source tables remain separate from analytics models. Milestone 2 does not replace or mutate the Milestone 1 persistence schema.

## Airflow Design

The `ecommerce_analytics_pipeline` DAG is intentionally orchestration-only:

1. wait for PostgreSQL;
2. check that operational source data exists;
3. run `dbt debug`;
4. run `dbt run`;
5. run `dbt test`.

Transformation logic stays in dbt SQL models rather than Python operators.

## Failure Handling

- Malformed events are rejected and logged without crashing the consumer.
- Duplicate `event_id`s are ignored after the first successful processing attempt.
- Database failures bubble out of the repository, are logged, and prevent offset commit.
- The system uses at-least-once delivery semantics with idempotent processing where practical.
