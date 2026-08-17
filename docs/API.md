# Analytics API

The FastAPI service is a read-only application layer over the dbt warehouse. It does not query the operational tables used by the Kafka consumer.

## Local startup

Build the warehouse first, then start the API:

```powershell
docker compose --profile analytics run --rm airflow-analytics
docker compose --profile dashboard up -d analytics-api
```

Open `http://localhost:8000/docs` for the generated OpenAPI UI.

## Endpoints

| Endpoint | Purpose | Warehouse source |
| --- | --- | --- |
| `GET /health` | API and database connectivity | PostgreSQL connection |
| `GET /api/v1/analytics/overview` | Revenue, orders, payments, customers, products, and shipment KPIs | All marts |
| `GET /api/v1/analytics/orders` | Daily order, gross value, and completed revenue trend | `fct_orders` |
| `GET /api/v1/analytics/products?limit=10` | Product units and revenue leaderboard | `dim_products` |
| `GET /api/v1/analytics/customers?limit=10` | Customer order and spend aggregates | `dim_customers` |
| `GET /api/v1/analytics/payments` | Payment status distribution and amounts | `fct_payments` |
| `GET /api/v1/analytics/shipments` | Shipment status distribution | `fct_orders` |

Orders accepts optional `start_date`, `end_date`, and bounded `limit` parameters. Leaderboard endpoints accept a bounded `limit`. SQL values are parameterized and aggregation remains in PostgreSQL.

The dashboard uses `VITE_API_BASE_URL` at build time. API database credentials stay server-side in `DATABASE_URL`; no secrets are sent to the frontend bundle.
