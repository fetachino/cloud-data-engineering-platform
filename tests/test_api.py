from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient
from psycopg import OperationalError

from services.api.app import app
from services.api.database import get_connection


class FakeResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def fetchone(self) -> dict[str, object] | None:
        return self.rows[0] if self.rows else None

    def fetchall(self) -> list[dict[str, object]]:
        return self.rows


class FakeConnection:
    def execute(self, query: str, params: object = None) -> FakeResult:
        if "select 1" in query:
            return FakeResult([{"?column?": 1}])
        if "completed_revenue" in query:
            return FakeResult([{
                "completed_revenue": Decimal("174.93"), "gross_order_value": Decimal("199.92"),
                "total_orders": 4, "completed_payments": 3, "failed_payments": 1,
                "average_order_value": Decimal("49.98"), "total_customers": 1, "total_products": 4,
                "delivered_shipments": 2, "total_shipments": 4,
            }])
        if "order_created_at::date" in query:
            return FakeResult([{
                "order_date": date(2026, 1, 1), "order_count": 4,
                "gross_order_value": Decimal("199.92"),
                "completed_revenue": Decimal("174.93"),
            }])
        if "dim_products" in query:
            return FakeResult([{
                "product_id": UUID("00000000-0000-0000-0000-000000000001"),
                "product_name": "Keyboard", "category": "Accessories", "units_ordered": 2,
                "gross_ordered_amount": Decimal("49.98"),
            }])
        if "dim_customers" in query:
            return FakeResult([{
                "customer_id": UUID("00000000-0000-0000-0000-000000000001"),
                "email": "a@example.com", "customer_name": "Ada Lovelace", "order_count": 4,
                "lifetime_completed_payment_amount": Decimal("174.93"),
                "average_order_value": Decimal("43.73"), "most_recent_order_at": None,
            }])
        if "payment_status" in query:
            return FakeResult([{"payment_status": "completed", "payment_count": 3,
                                "total_amount": Decimal("174.93")}])
        return FakeResult([{"shipment_status": "delivered", "shipment_count": 2}])


def fake_connection():
    yield FakeConnection()


app.dependency_overrides[get_connection] = fake_connection
client = TestClient(app)


def test_health_reports_database_connection() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_overview_exposes_warehouse_kpis() -> None:
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    assert response.json()["completed_revenue"] == 174.93
    assert response.json()["total_orders"] == 4


def test_orders_reject_invalid_date_range_and_limit() -> None:
    response = client.get(
        "/api/v1/analytics/orders?start_date=2026-02-01&end_date=2026-01-01"
    )
    assert response.status_code == 400
    assert client.get("/api/v1/analytics/products?limit=0").status_code == 422


def test_products_and_payment_responses_are_typed() -> None:
    products_response = client.get("/api/v1/analytics/products")
    payments_response = client.get("/api/v1/analytics/payments")
    assert products_response.json()[0]["product_name"] == "Keyboard"
    assert payments_response.json()[0]["payment_count"] == 3


def test_warehouse_failure_returns_safe_service_error() -> None:
    class FailingConnection:
        def execute(self, query: str, params: object = None) -> None:
            raise OperationalError("connection failed")

    def failing_connection():
        yield FailingConnection()

    app.dependency_overrides[get_connection] = failing_connection
    try:
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 503
        assert response.json() == {"detail": "Warehouse unavailable"}
    finally:
        app.dependency_overrides[get_connection] = fake_connection
