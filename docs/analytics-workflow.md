# Analytics Workflow

Milestone 2 adds a local analytics workflow on top of the Milestone 1 operational pipeline.

## Run Order

1. Start PostgreSQL, Kafka, migrations, and the consumer.
2. Produce deterministic source events.
3. Run dbt directly or through Airflow.
4. Query the `analytics` schema.

## Commands

```powershell
docker compose up -d postgres kafka kafka-init migrate consumer
docker compose --profile producer run --rm producer
docker compose --profile analytics run --rm airflow-analytics
```

For direct dbt execution:

```powershell
docker compose --profile analytics run --rm analytics-dbt
```

## Data Quality

dbt tests cover source relationships, not-null and unique keys, accepted status values, and business rules such as non-negative order and payment amounts. The Airflow DAG runs `dbt test` after the models are built.
