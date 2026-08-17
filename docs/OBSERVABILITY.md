# Local Observability

Milestone 4 adds production-style visibility to the local pipeline without changing its delivery or transformation semantics.

## What is monitored

| Area | Signals | Source |
| --- | --- | --- |
| Ingestion | received, processed, duplicate, malformed, failed events, processing duration | Consumer `/metrics` on port 9101 |
| API | request count/status, in-flight requests, request latency, database failures and query latency | FastAPI `/metrics` |
| Kafka | broker availability, topic/partition metrics, consumer-group lag | Kafka exporter |
| PostgreSQL | database availability, active connections, database activity | PostgreSQL exporter |
| Platform | scrape target health and threshold rules | Prometheus |

Metric labels are deliberately bounded. Routes are declared route templates, statuses are HTTP codes, and consumer results are a small fixed vocabulary; event IDs, customer IDs, correlation IDs, URLs with query strings, and exception messages are never metric labels.

## Start the stack

Create `.env` from `.env.example`, then run the normal pipeline and warehouse workflow:

```powershell
docker compose up -d postgres kafka migrate consumer
docker compose --profile producer run --rm producer --event-count 25 --rate-per-second 20 --seed 42
docker compose --profile analytics run --rm airflow-analytics
docker compose --profile dashboard --profile observability up -d
```

Open:

- API metrics: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Grafana is provisioned with the Prometheus datasource and the `Cloud Data Platform Observability` dashboard. The default local login is controlled by `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`; these are example development values only.

## Dashboard panels

The dashboard focuses on a recruiter-readable operational story: scrape health, Kafka consumer lag, ingestion throughput, consumer/API p95 latency, API status rates, pipeline failures, PostgreSQL activity, and API activity.

## Thresholds

Prometheus rules document realistic local warning conditions:

- API, consumer, or exporter target down for two minutes;
- consumer lag above 10 records for five minutes;
- API 5xx rate above 0.1 responses per second for five minutes.

These are reviewable operational starting points, not a paging system. Alertmanager and production notification routing are intentionally outside this local milestone.

## Logging strategy and limitations

Python services emit JSON logs with timestamp, level, logger name, message, and contextual fields. Ingestion logs preserve event, correlation, type, and processing result fields. API request logs add a generated or propagated `request_id`, method, route template, status, and duration. Secrets, credentials, connection strings, and arbitrary payloads are excluded.

Airflow is currently run as a one-shot local DAG test that executes dbt debug/run/test. There is no continuously running scheduler or honest scheduler uptime metric to monitor yet. A production deployment would add centralized log retention, Alertmanager routing, exporter authentication/network policy, and durable metric storage.
