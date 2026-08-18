# Interview Guide

## Architecture tradeoffs

The project separates operational ingestion tables from the analytics schema.
That keeps event processing reliable and lets dbt own reusable business
transformations while FastAPI remains a thin read-only serving layer.

## Kafka and delivery semantics

Kafka provides durable buffering and decouples production from persistence.
The consumer is intentionally at-least-once: it commits an offset only after a
malformed-event decision or successful database transaction. The
`processed_events` primary key makes retries harmless, but the system does not
claim distributed exactly-once delivery.

## Airflow and dbt

Airflow handles ordering, readiness, and execution of `dbt debug`, `dbt run`,
and `dbt test`; SQL transformation logic stays in dbt models. Dimensional marts
make dashboard queries stable and testable.

## Observability

The API and consumer expose bounded Prometheus metrics, while exporters cover
Kafka and PostgreSQL. Structured logs carry request/event context without raw
payloads or credentials. Grafana provides a single local operational view.

## AWS and cost decisions

One Fargate task, single-AZ RDS, no NAT Gateway, no MSK, and no MWAA keep the
portfolio deployment understandable and reduce fixed cost. The tradeoff is
that it is not highly available or a hosted Kafka/Airflow platform.

## Security

RDS is private, S3 public access is blocked, containers run non-root, and
GitHub Actions uses an immutable repository-ID/environment OIDC subject rather
than long-lived AWS keys. The public ALB is HTTP-only because no domain or
certificate was provisioned.

## Limitations and next steps

The system has one Kafka partition, one API task, local Terraform state, no
dead-letter topic, and no measured performance baseline. A production version
would add remote encrypted state, HTTPS, stronger egress controls, replay/DLQ
operations, migration automation, and load testing.
