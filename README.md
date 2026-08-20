# Cloud Data Engineering Platform

[![CI](https://github.com/fetachino/cloud-data-engineering-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/fetachino/cloud-data-engineering-platform/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Apache Kafka](https://img.shields.io/badge/Kafka-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![dbt](https://img.shields.io/badge/dbt-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white)](https://aws.amazon.com/)

An end-to-end e-commerce data platform built to demonstrate reliable event
ingestion, analytics engineering, a read-only serving layer, observability,
and a cost-conscious AWS deployment. The system uses deterministic synthetic
events, so every local demo is repeatable and contains no real customer data.

## What It Demonstrates

- Versioned Pydantic event contracts and deterministic Kafka production
- At-least-once ingestion with transactional PostgreSQL writes and `event_id`
  idempotency
- Airflow orchestration of dbt staging, intermediate, and dimensional models
- FastAPI analytics endpoints backed by the `analytics` warehouse schema
- React and TypeScript dashboard for revenue, orders, payments, products, and
  fulfillment
- Prometheus metrics, Kafka/PostgreSQL exporters, Grafana dashboards, and
  structured logs
- Terraform-managed AWS infrastructure and GitHub Actions deployment through
  short-lived OIDC credentials

This is a portfolio environment, not a claim of production-scale throughput,
availability, or performance.

## What this proves

- Reliable event ingestion with schema contracts, at-least-once delivery, and
  database idempotency
- Analytics engineering with Airflow orchestration, dbt models, and a
  read-only serving layer
- Practical observability through metrics, exporters, dashboards, and logs
- Cost-conscious cloud design using Terraform and short-lived GitHub OIDC
  credentials

The local demo is the primary reproducible path. The AWS materials document an
optional deployment design and workflow; they are not a claim of a continuously
hosted production service or measured production performance.

## Architecture

```mermaid
flowchart LR
    producer[Deterministic synthetic producer] --> kafka[Kafka\necommerce.events.v1]
    kafka --> consumer[Python consumer\nvalidation + idempotency]
    consumer --> postgres[(PostgreSQL\noperational schema)]
    postgres --> airflow[Airflow one-shot workflow]
    airflow --> dbt[dbt transformations]
    dbt --> warehouse[(PostgreSQL\nanalytics schema)]
    warehouse --> api[FastAPI\nread-only analytics API]
    api --> dashboard[React + TypeScript\ndashboard]

    consumer -. metrics .-> prometheus[Prometheus]
    api -. metrics .-> prometheus
    kafka -. exporter .-> prometheus
    postgres -. exporter .-> prometheus
    prometheus --> grafana[Grafana]
```

The deployed AWS path is intentionally separate from the local Kafka and
Airflow stack:

```mermaid
flowchart LR
    github[GitHub Actions\nOIDC + protected portfolio environment]
    github --> ecr[ECR immutable API image]
    ecr --> ecs[ECS Fargate\none API task]
    ecs --> rds[(Private RDS PostgreSQL)]
    alb[Public HTTP ALB] --> ecs
    s3[Private S3 frontend bucket] --> cloudfront[CloudFront]
    cw[CloudWatch logs]
    ecs --> cw
    secrets[Secrets Manager] --> ecs
```

The AWS design uses one region, no NAT Gateway, no MSK, and no MWAA. Kafka,
Airflow, and dbt remain local or controlled-job components to avoid paying for
always-on managed services in a portfolio deployment.

## Technology Stack

Python 3.11, Pydantic, confluent-kafka, PostgreSQL, Alembic, Airflow, dbt,
FastAPI, React, TypeScript, Vite, Recharts, Docker Compose, Prometheus,
Grafana, Terraform, ECS/Fargate, RDS, ECR, S3, CloudFront, CloudWatch, IAM,
GitHub Actions, and GitHub OIDC.

## Local Quick Start

```powershell
Copy-Item .env.example .env
docker compose up -d postgres kafka migrate consumer
docker compose --profile producer run --rm producer
docker compose --profile analytics run --rm analytics-dbt
docker compose --profile dashboard up -d analytics-api frontend
```

Open `http://localhost:5173` for the dashboard or
`http://localhost:8000/docs` for the API. Add observability with:

```powershell
docker compose --profile dashboard --profile observability up -d
```

Grafana is at `http://localhost:3000` and Prometheus is at
`http://localhost:9090`. The full reproducible demo is in
[docs/DEMO.md](docs/DEMO.md).

## Verified Results

The deterministic 25-event local run produced:

| Entity | Rows |
| --- | ---: |
| Processed events | 25 |
| Customers | 1 |
| Products | 4 |
| Orders | 4 |
| Order items | 4 |
| Payments | 4 |
| Inventory records | 4 |
| Shipments | 2 |

Replaying the same events kept every count unchanged, demonstrating the
`processed_events.event_id` idempotency guard.

## Portfolio Screenshots

### Deployed CloudFront frontend

![CloudFront frontend with populated analytics](docs/images/cloudfront-frontend.png)

### Grafana observability dashboard

![Grafana observability dashboard](docs/images/grafana.png)

The current portfolio endpoints and optional AWS deployment workflow are
documented in [docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) without exposing
credentials or secret values.

## Verification

The repository includes automated Python and frontend tests, Ruff, mypy,
frontend lint/build, Compose configuration checks, Alembic SQL generation,
dbt tests, Airflow DAG regression tests, Terraform formatting/validation, and
Docker builds. Run the focused local suite with:

```powershell
pytest
ruff check .
mypy
alembic upgrade head --sql
docker compose config
docker compose --profile analytics config
docker compose --profile dashboard config
docker compose --profile observability config
Set-Location frontend
npm.cmd ci
npm.cmd run test
npm.cmd run lint
npm.cmd run build
Set-Location ..
```

See [docs/DEMO.md](docs/DEMO.md) for the complete verification sequence and
[docs/images/README.md](docs/images/README.md) for the evidence capture list.

## Security Decisions

- Synthetic data uses `example.test`; secrets stay in environment variables or
  AWS Secrets Manager and Terraform state stays outside Git.
- The GitHub deployment role trusts the immutable repository/environment OIDC
  subject and preserves the `sts.amazonaws.com` audience.
- ECS application and consumer images run as non-root users.
- RDS is private and its security group accepts PostgreSQL only from the API
  task security group.
- S3 public access is blocked and CloudFront uses origin access control.
- GitHub Actions uses `contents: read` and short-lived OIDC credentials rather
  than long-lived AWS access keys.

The public ALB is HTTP-only because no domain or certificate is provisioned;
the API is read-only and serves synthetic analytics. See
[SECURITY.md](SECURITY.md) for the residual risks and next steps.

## Status and Limitations

All five major milestones are complete and merged. Remaining limitations are
deliberate portfolio tradeoffs: one Kafka partition, one Fargate task, single-
AZ RDS, no HTTPS custom domain, no dead-letter topic, local/controlled-job
Airflow and dbt, local Terraform state, and no measured performance benchmark.

Recommended next production steps would be remote encrypted Terraform state,
HTTPS with a managed certificate, stronger network egress controls, a dead-
letter/replay workflow, automated migration operations, and load testing.

## Further Reading

- [Architecture](ARCHITECTURE.md)
- [AWS deployment](docs/AWS_DEPLOYMENT.md)
- [CI/CD and OIDC](docs/CI_CD.md)
- [Demo guide](docs/DEMO.md)
