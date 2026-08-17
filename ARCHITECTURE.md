# Architecture

## Current Scope

The project currently includes the local event pipeline, analytics transformation layer, and Milestone 3 application layer:

```text
services/producer
  -> Kafka
  -> services/consumer
  -> PostgreSQL operational tables
  -> Airflow
  -> dbt staging/intermediate models
  -> dbt dimensional marts in the analytics schema
  -> FastAPI analytics API
  -> React + TypeScript dashboard
```

## Service Boundaries

- `shared/`: event contracts, configuration, and logging helpers
- `services/producer/`: deterministic synthetic event generation and Kafka publishing
- `services/consumer/`: Kafka consumption, validation, idempotency, and persistence
- `db/migrations/`: Alembic-managed operational schema
- `analytics/`: dbt project for staging, intermediate, and mart models
- `airflow/dags/`: orchestration for the local analytics transformation workflow
- `services/api/`: read-only FastAPI service, response models, warehouse queries, and database dependency
- `frontend/`: Vite React/TypeScript dashboard and API client
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

## Application Layer

The API queries dbt marts directly, keeping business metrics in the warehouse rather than duplicating logic in Python. `analytics.fct_orders` supplies order totals and order trends, `analytics.fct_payments` supplies payment status and completed revenue, `analytics.dim_products` supplies the product leaderboard, and `analytics.dim_customers` supplies customer aggregates. Shipment status is exposed from the order fact where present.

The dashboard calls the API through one typed client and never connects directly to PostgreSQL. The Compose `dashboard` profile serves the API on port 8000 and the built frontend through nginx on port 5173. CORS is limited to the local frontend origins configured in `API_CORS_ORIGINS`.

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
