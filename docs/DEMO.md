# Recruiter Demo

This is a 2-4 minute path through the project. It uses deterministic synthetic
events and can be shown locally without AWS credentials.

## 1. Explain the architecture

Start with the Mermaid diagram in [README.md](../README.md): events move from
Kafka through an idempotent Python consumer into PostgreSQL, then Airflow/dbt
build the analytics schema consumed by FastAPI and React. Point out that
Prometheus and Grafana observe the pipeline separately.

## 2. Start the local stack

```powershell
Copy-Item .env.example .env
docker compose up -d postgres kafka migrate consumer
docker compose --profile dashboard up -d analytics-api frontend
docker compose --profile dashboard --profile observability up -d
```

## 3. Generate and inspect events

```powershell
docker compose --profile producer run --rm producer
docker compose exec postgres psql -U platform -d ecommerce -c "select event_type, count(*) from processed_events group by event_type order by event_type;"
```

For the recorded evidence run, `EVENT_COUNT=25` and the deterministic seed
produced 25 processed events. Re-running the same event IDs leaves the domain
counts unchanged because `processed_events.event_id` is the idempotency ledger.

## 4. Build and explain the warehouse

```powershell
docker compose --profile analytics run --rm analytics-dbt
docker compose --profile analytics run --rm airflow-analytics
docker compose exec postgres psql -U platform -d ecommerce -c "select count(*) from analytics.fct_orders;"
```

Show the staging, intermediate, and mart SQL under `analytics/models/`, then
explain that the API reads the modeled `analytics` schema rather than raw
operational tables.

## 5. Show the API and dashboard

- Open `http://localhost:8000/docs` and call a read-only analytics endpoint.
- Open `http://localhost:5173` and point out KPI cards, revenue trend, payment
  status, product ranking, and fulfillment views.

## 6. Show observability

- Open `http://localhost:3000` and show the provisioned Grafana dashboard.
- Open `http://localhost:9090` to show Prometheus targets and metrics.
- Explain bounded labels, request IDs, ingestion outcomes, and latency metrics.

## 7. Close with cloud evidence

Show the Terraform layout and GitHub Actions workflow. The verified portfolio
deployment uses one `us-east-1` VPC, private RDS, one ECS/Fargate API task,
ECR, a private S3 bucket behind CloudFront, CloudWatch logs, Secrets Manager,
and immutable GitHub OIDC trust. It deliberately avoids MSK, MWAA, and a NAT
Gateway.

The currently verified public endpoints are:

- Frontend: `https://d2obbvybkww8y5.cloudfront.net`
- API: `http://cloud-data-platform-portf-alb-1313910402.us-east-1.elb.amazonaws.com`

Do not display Terraform state, database credentials, AWS access keys, or
GitHub tokens during a demo.
