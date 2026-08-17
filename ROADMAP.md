# Roadmap

## Milestone 1: Local Event Pipeline Foundation

Implemented in this repository.

## Milestone 2: Analytics Transformation Layer

Implemented in this repository:

- Airflow orchestration
- dbt transformations
- Analytics warehouse layer
- Data-quality checks
- Dimensional models

## Milestone 3: Analytics API and Dashboard

Implemented in this repository:

- FastAPI analytics API backed by dbt marts
- React/TypeScript dashboard served by nginx
- Business KPIs, order trend, payment status, product, and fulfillment views
- API and frontend tests plus Docker Compose dashboard profile

## Milestone 4: Observability

Implemented in this repository:

- Prometheus API and ingestion metrics
- Kafka and PostgreSQL exporters
- Provisioned Grafana datasource and pipeline health dashboard
- Structured request and event logging
- Documented operational thresholds

## Milestone 5: Cloud Deployment

Implemented as an unapplied, reviewable deployment layer:

- Terraform VPC, ECR, ECS Fargate, private RDS, CloudWatch, S3, and CloudFront
- IAM roles with GitHub OIDC deployment trust
- Non-root production containers with immutable image tags
- GitHub Actions CI and controlled deployment workflow
- Documented costs, state strategy, security posture, deployment, and teardown

AWS apply and endpoint verification require an authenticated account and are not
claimed by the current repository state.
