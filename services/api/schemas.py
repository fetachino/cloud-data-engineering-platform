"""Public response models for the analytics API."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["connected", "unavailable"]


class OverviewResponse(BaseModel):
    completed_revenue: Decimal = Field(ge=0)
    gross_order_value: Decimal = Field(ge=0)
    total_orders: int = Field(ge=0)
    completed_payments: int = Field(ge=0)
    failed_payments: int = Field(ge=0)
    average_order_value: Decimal | None = Field(default=None, ge=0)
    total_customers: int = Field(ge=0)
    total_products: int = Field(ge=0)
    delivered_shipments: int = Field(ge=0)
    total_shipments: int = Field(ge=0)


class OrderAnalytics(BaseModel):
    order_date: date
    order_count: int = Field(ge=0)
    gross_order_value: Decimal = Field(ge=0)
    completed_revenue: Decimal = Field(ge=0)


class ProductAnalytics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    product_name: str
    category: str
    units_ordered: int = Field(ge=0)
    gross_ordered_amount: Decimal = Field(ge=0)


class CustomerAnalytics(BaseModel):
    customer_id: UUID
    email: str
    customer_name: str
    order_count: int = Field(ge=0)
    lifetime_completed_payment_amount: Decimal = Field(ge=0)
    average_order_value: Decimal | None = Field(default=None, ge=0)
    most_recent_order_at: datetime | None = None


class PaymentStatusAnalytics(BaseModel):
    payment_status: str
    payment_count: int = Field(ge=0)
    total_amount: Decimal = Field(ge=0)


class ShipmentStatusAnalytics(BaseModel):
    shipment_status: str
    shipment_count: int = Field(ge=0)

