from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationInfo, field_validator


class EventType(StrEnum):
    CUSTOMER_CREATED = "customer_created"
    PRODUCT_CREATED = "product_created"
    ORDER_CREATED = "order_created"
    ORDER_ITEM_ADDED = "order_item_added"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    INVENTORY_ADJUSTED = "inventory_adjusted"
    SHIPMENT_CREATED = "shipment_created"
    SHIPMENT_DELIVERED = "shipment_delivered"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CustomerCreatedPayload(StrictModel):
    customer_id: UUID
    email: str = Field(pattern=r"^[a-z0-9._%+-]+@example\.test$")
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    country: str = Field(min_length=2, max_length=2)


class ProductCreatedPayload(StrictModel):
    product_id: UUID
    sku: str = Field(min_length=3)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class OrderCreatedPayload(StrictModel):
    order_id: UUID
    customer_id: UUID
    status: Literal["created"]
    currency: Literal["USD"]


class OrderItemAddedPayload(StrictModel):
    order_item_id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0, le=20)
    unit_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class PaymentCompletedPayload(StrictModel):
    payment_id: UUID
    order_id: UUID
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: Literal["USD"]
    provider: Literal["stripe_test", "adyen_test", "paypal_test"]


class PaymentFailedPayload(StrictModel):
    payment_id: UUID
    order_id: UUID
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: Literal["USD"]
    provider: Literal["stripe_test", "adyen_test", "paypal_test"]
    failure_code: Literal["insufficient_funds", "card_declined", "gateway_timeout"]


class InventoryAdjustedPayload(StrictModel):
    inventory_event_id: UUID
    product_id: UUID
    quantity_delta: int = Field(ge=-500, le=500)
    reason: Literal["initial_stock", "order_reserved", "return_received", "manual_correction"]


class ShipmentCreatedPayload(StrictModel):
    shipment_id: UUID
    order_id: UUID
    carrier: Literal["ups_test", "fedex_test", "usps_test"]
    tracking_number: str = Field(min_length=8)
    status: Literal["created"]


class ShipmentDeliveredPayload(StrictModel):
    shipment_id: UUID
    order_id: UUID
    delivered_at: datetime
    status: Literal["delivered"]

    @field_validator("delivered_at")
    @classmethod
    def delivered_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("delivered_at must include timezone information")
        return value


Payload: TypeAlias = (
    CustomerCreatedPayload
    | ProductCreatedPayload
    | OrderCreatedPayload
    | OrderItemAddedPayload
    | PaymentCompletedPayload
    | PaymentFailedPayload
    | InventoryAdjustedPayload
    | ShipmentCreatedPayload
    | ShipmentDeliveredPayload
)


class EcommerceEvent(StrictModel):
    event_id: UUID
    event_type: EventType
    event_version: Literal[1]
    occurred_at: datetime
    producer: str = Field(min_length=1)
    correlation_id: UUID
    payload: Payload

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("occurred_at must include timezone information")
        return value.astimezone(UTC)

    @field_validator("payload")
    @classmethod
    def payload_must_match_event_type(cls, value: Payload, info: ValidationInfo) -> Payload:
        event_type = info.data.get("event_type")
        expected_payloads: dict[EventType, type[Payload]] = {
            EventType.CUSTOMER_CREATED: CustomerCreatedPayload,
            EventType.PRODUCT_CREATED: ProductCreatedPayload,
            EventType.ORDER_CREATED: OrderCreatedPayload,
            EventType.ORDER_ITEM_ADDED: OrderItemAddedPayload,
            EventType.PAYMENT_COMPLETED: PaymentCompletedPayload,
            EventType.PAYMENT_FAILED: PaymentFailedPayload,
            EventType.INVENTORY_ADJUSTED: InventoryAdjustedPayload,
            EventType.SHIPMENT_CREATED: ShipmentCreatedPayload,
            EventType.SHIPMENT_DELIVERED: ShipmentDeliveredPayload,
        }
        is_mismatched_payload = isinstance(event_type, EventType) and not isinstance(
            value,
            expected_payloads[event_type],
        )
        if is_mismatched_payload:
            raise ValueError(f"payload does not match event_type {event_type}")
        return value


def validate_event(raw_event: bytes | str | dict[str, object]) -> EcommerceEvent:
    if isinstance(raw_event, bytes):
        raw_event = raw_event.decode("utf-8")
    if isinstance(raw_event, str):
        return TypeAdapter(EcommerceEvent).validate_json(raw_event)
    return EcommerceEvent.model_validate(raw_event)
