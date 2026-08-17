# Cloud Data Engineering Platform

This is a recruiter-quality portfolio project that demonstrates a local foundation for an e-commerce data platform. Milestone 1 implements a deterministic synthetic event pipeline from producer to Kafka to a Python ingestion consumer to PostgreSQL.

It is intentionally honest about scope: this is a portfolio system, not a production-scale or enterprise-live platform.

## Current Status

Milestone 1: Local Event Pipeline Foundation.

Implemented:

- Typed e-commerce event contracts with Pydantic
- Deterministic synthetic event generation
- Kafka topic `ecommerce.events.v1`
- Python consumer with schema validation and structured logs
- PostgreSQL operational schema with Alembic migrations
- Idempotent event processing through `processed_events.event_id`
- Docker Compose local stack
- Focused unit tests

Not implemented yet:

- Airflow, dbt, analytics warehouse
- FastAPI analytics API
- React dashboard
- Prometheus/Grafana
- Terraform/AWS/CI deployment

## Local Architecture

```text
Synthetic producer
  -> Kafka topic ecommerce.events.v1
  -> Python consumer
  -> PostgreSQL operational tables
```

The local Kafka topic uses one partition to preserve ordering for related order lifecycle events in this portfolio-sized setup. Producers use `correlation_id` as the Kafka message key.

## Technology Stack

- Python 3.11
- Pydantic
- confluent-kafka
- PostgreSQL
- Alembic
- Docker Compose
- Pytest
- Ruff
- mypy

## Run Locally

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Start the broker, database, migrations, and consumer:

```powershell
docker compose up -d postgres kafka migrate consumer
```

Produce sample events:

```powershell
docker compose --profile producer run --rm producer
```

Inspect processed events:

```powershell
docker compose exec postgres psql -U platform -d ecommerce -c "select event_type, count(*) from processed_events group by event_type order by event_type;"
```

Run tests and checks locally:

```powershell
pytest
ruff check .
mypy
docker compose config
```

## Delivery Semantics

The consumer validates each event before persistence. Valid events are written inside a database transaction that first claims the `event_id` in `processed_events`. If the event was already processed, the consumer treats it as a harmless duplicate.

Offsets are committed only after validation rejection or successful duplicate/domain processing. This is at-least-once processing with idempotent writes where practical. It does not claim exactly-once delivery.

## Limitations

- Local Docker Compose only
- Single Kafka partition for simple local ordering
- No dead-letter topic yet
- No cloud infrastructure yet
- No measured performance benchmarks
- No production uptime or scale claims

See [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), and [SECURITY.md](SECURITY.md).
