"""HTTP routes for health and warehouse analytics."""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg import Connection, OperationalError

from services.api.database import check_connection, get_connection
from services.api.queries import (
    fetch_customers,
    fetch_orders,
    fetch_overview,
    fetch_payment_statuses,
    fetch_products,
    fetch_shipment_statuses,
)
from services.api.schemas import (
    CustomerAnalytics,
    HealthResponse,
    OrderAnalytics,
    OverviewResponse,
    PaymentStatusAnalytics,
    ProductAnalytics,
    ShipmentStatusAnalytics,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health(connection: Annotated[Connection[Any], Depends(get_connection)]) -> HealthResponse:
    try:
        check_connection(connection)
    except OperationalError:
        return HealthResponse(status="degraded", database="unavailable")
    return HealthResponse(status="ok", database="connected")


@router.get("/api/v1/analytics/overview", response_model=OverviewResponse, tags=["analytics"])
def overview(connection: Annotated[Connection[Any], Depends(get_connection)]) -> OverviewResponse:
    try:
        return OverviewResponse(**fetch_overview(connection))
    except OperationalError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Warehouse unavailable"
        ) from error


@router.get("/api/v1/analytics/orders", response_model=list[OrderAnalytics], tags=["analytics"])
def orders(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=90, ge=1, le=365),
) -> list[OrderAnalytics]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    return [OrderAnalytics(**row) for row in fetch_orders(connection, start_date, end_date, limit)]


@router.get("/api/v1/analytics/products", response_model=list[ProductAnalytics], tags=["analytics"])
def products(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ProductAnalytics]:
    return [ProductAnalytics(**row) for row in fetch_products(connection, limit)]


@router.get(
    "/api/v1/analytics/customers", response_model=list[CustomerAnalytics], tags=["analytics"]
)
def customers(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: int = Query(default=10, ge=1, le=100),
) -> list[CustomerAnalytics]:
    return [CustomerAnalytics(**row) for row in fetch_customers(connection, limit)]


@router.get(
    "/api/v1/analytics/payments", response_model=list[PaymentStatusAnalytics], tags=["analytics"]
)
def payments(
    connection: Annotated[Connection[Any], Depends(get_connection)]
) -> list[PaymentStatusAnalytics]:
    return [PaymentStatusAnalytics(**row) for row in fetch_payment_statuses(connection)]


@router.get(
    "/api/v1/analytics/shipments", response_model=list[ShipmentStatusAnalytics], tags=["analytics"]
)
def shipments(
    connection: Annotated[Connection[Any], Depends(get_connection)]
) -> list[ShipmentStatusAnalytics]:
    return [ShipmentStatusAnalytics(**row) for row in fetch_shipment_statuses(connection)]
