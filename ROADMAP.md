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

Implemented and verified as a cost-conscious portfolio deployment layer:

- Terraform VPC, ECR, ECS Fargate, private RDS, CloudWatch, S3, and CloudFront
- IAM roles with GitHub OIDC deployment trust
- Non-root production containers with immutable image tags
- GitHub Actions CI and controlled deployment workflow
- Documented costs, state strategy, security posture, deployment, and teardown

The deployment was applied and endpoint verification was completed in the
authenticated `us-east-1` portfolio account. Final hardening remains
documentation, evidence, dependency review, and presentation work; it does not
add another major subsystem.
