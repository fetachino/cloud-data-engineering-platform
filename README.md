# Cloud Data Engineering Platform

This is a recruiter-quality portfolio project that demonstrates a local e-commerce data platform from event ingestion through an analytics dashboard. It implements deterministic event ingestion, Airflow/dbt transformations, a read-only FastAPI analytics API, and a React dashboard.

It is intentionally honest about scope: this is a portfolio system, not a production-scale or enterprise-live platform.

## Current Status

Milestone 3: Analytics API and React Dashboard.

Implemented:

- Typed e-commerce event contracts with Pydantic
- Deterministic synthetic event generation
- Kafka topic `ecommerce.events.v1`
- Python consumer with schema validation and structured logs
- PostgreSQL operational schema with Alembic migrations
- Idempotent event processing through `processed_events.event_id`
- Docker Compose local stack
- dbt staging, intermediate, and dimensional mart models
- Dedicated PostgreSQL `analytics` schema
- Airflow orchestration for dbt run/test workflow
- Data-quality tests for schema constraints and business rules
- FastAPI analytics API backed by dbt marts
- React + TypeScript dashboard with KPI cards, revenue trend, payment status, product, and fulfillment views
- Focused unit tests

Not implemented yet:

- Prometheus/Grafana
- Terraform/AWS/CI deployment

## Local Architecture

```text
Synthetic producer
  -> Kafka topic ecommerce.events.v1
  -> Python consumer
  -> PostgreSQL operational tables
  -> Airflow-orchestrated dbt models
  -> PostgreSQL analytics schema
  -> FastAPI analytics API
  -> React + TypeScript dashboard
```

The local Kafka topic uses one partition to preserve ordering for related order lifecycle events in this portfolio-sized setup. Producers use `correlation_id` as the Kafka message key.

## Technology Stack

- Python 3.11
- Pydantic
- confluent-kafka
- PostgreSQL
- Alembic
- dbt-postgres
- Apache Airflow
- FastAPI and Uvicorn
- React, TypeScript, Vite, and Recharts
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

Run dbt directly after source data exists:

```powershell
docker compose --profile analytics run --rm analytics-dbt
```

Run the Airflow-orchestrated analytics workflow:

```powershell
docker compose --profile analytics run --rm airflow-analytics
```

Start the read-only API and dashboard after the warehouse has been built:

```powershell
docker compose --profile dashboard up -d analytics-api frontend
```

Open `http://localhost:5173` for the dashboard or `http://localhost:8000/docs` for the API documentation. The API reads only from the modeled `analytics` schema.

Inspect processed events:

```powershell
docker compose exec postgres psql -U platform -d ecommerce -c "select event_type, count(*) from processed_events group by event_type order by event_type;"
```

Inspect analytics marts:

```powershell
docker compose exec postgres psql -U platform -d ecommerce -c "select count(*) from analytics.fct_orders;"
```

Run tests and checks locally:

```powershell
pytest
ruff check .
mypy
docker compose config
docker compose --profile analytics config
docker compose --profile dashboard config
Set-Location frontend
npm.cmd install
npm.cmd run test
npm.cmd run lint
npm.cmd run build
Set-Location ..
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

See [docs/warehouse-model.md](docs/warehouse-model.md) for the dbt model layout and key decisions.
