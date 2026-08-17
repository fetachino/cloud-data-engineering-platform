from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from psycopg import Connection
from psycopg.rows import dict_row

from shared.events.models import (
    CustomerCreatedPayload,
    EcommerceEvent,
    EventType,
    InventoryAdjustedPayload,
    OrderCreatedPayload,
    OrderItemAddedPayload,
    PaymentCompletedPayload,
    PaymentFailedPayload,
    ProductCreatedPayload,
    ShipmentCreatedPayload,
    ShipmentDeliveredPayload,
)


class ConnectionFactory(Protocol):
    def __call__(self) -> Connection[dict[str, object]]: ...


@dataclass(frozen=True)
class ProcessResult:
    processed: bool
    reason: str


class EventRepository:
    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def process_event(self, event: EcommerceEvent) -> ProcessResult:
        with self.connection_factory() as connection, connection.transaction():
            inserted = self._claim_event(connection, event)
            if not inserted:
                return ProcessResult(processed=False, reason="duplicate_event")
            self._apply_event(connection, event)
        return ProcessResult(processed=True, reason="processed")

    def _claim_event(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
    ) -> bool:
        result = connection.execute(
            """
            INSERT INTO processed_events (event_id, event_type, event_version, correlation_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
            RETURNING event_id
            """,
            (event.event_id, event.event_type.value, event.event_version, event.correlation_id),
        ).fetchone()
        return result is not None

    def _apply_event(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
    ) -> None:
        match event.event_type:
            case EventType.CUSTOMER_CREATED:
                assert isinstance(event.payload, CustomerCreatedPayload)
                self._upsert_customer(connection, event, event.payload)
            case EventType.PRODUCT_CREATED:
                assert isinstance(event.payload, ProductCreatedPayload)
                self._upsert_product(connection, event, event.payload)
            case EventType.ORDER_CREATED:
                assert isinstance(event.payload, OrderCreatedPayload)
                self._upsert_order(connection, event, event.payload)
            case EventType.ORDER_ITEM_ADDED:
                assert isinstance(event.payload, OrderItemAddedPayload)
                self._upsert_order_item(connection, event, event.payload)
            case EventType.PAYMENT_COMPLETED:
                assert isinstance(event.payload, PaymentCompletedPayload)
                self._upsert_payment(connection, event, event.payload, "completed")
            case EventType.PAYMENT_FAILED:
                assert isinstance(event.payload, PaymentFailedPayload)
                self._upsert_payment(connection, event, event.payload, "failed")
            case EventType.INVENTORY_ADJUSTED:
                assert isinstance(event.payload, InventoryAdjustedPayload)
                self._insert_inventory_adjustment(connection, event, event.payload)
            case EventType.SHIPMENT_CREATED:
                assert isinstance(event.payload, ShipmentCreatedPayload)
                self._upsert_shipment(connection, event, event.payload)
            case EventType.SHIPMENT_DELIVERED:
                assert isinstance(event.payload, ShipmentDeliveredPayload)
                self._mark_shipment_delivered(connection, event.payload)

    def _upsert_customer(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: CustomerCreatedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO customers (customer_id, email, first_name, last_name, country, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET
                email = EXCLUDED.email,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                country = EXCLUDED.country
            """,
            (
                payload.customer_id,
                payload.email,
                payload.first_name,
                payload.last_name,
                payload.country,
                event.occurred_at,
            ),
        )

    def _upsert_product(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: ProductCreatedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO products (product_id, sku, name, category, price, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                sku = EXCLUDED.sku,
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                price = EXCLUDED.price
            """,
            (
                payload.product_id,
                payload.sku,
                payload.name,
                payload.category,
                payload.price,
                event.occurred_at,
            ),
        )

    def _upsert_order(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: OrderCreatedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO orders (order_id, customer_id, status, currency, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE SET
                customer_id = EXCLUDED.customer_id,
                status = EXCLUDED.status,
                currency = EXCLUDED.currency
            """,
            (
                payload.order_id,
                payload.customer_id,
                payload.status,
                payload.currency,
                event.occurred_at,
            ),
        )

    def _upsert_order_item(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: OrderItemAddedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO order_items (
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_item_id) DO UPDATE SET
                order_id = EXCLUDED.order_id,
                product_id = EXCLUDED.product_id,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price
            """,
            (
                payload.order_item_id,
                payload.order_id,
                payload.product_id,
                payload.quantity,
                payload.unit_price,
                event.occurred_at,
            ),
        )

    def _upsert_payment(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: PaymentCompletedPayload | PaymentFailedPayload,
        status: str,
    ) -> None:
        failure_code = payload.failure_code if isinstance(payload, PaymentFailedPayload) else None
        connection.execute(
            """
            INSERT INTO payments (
                payment_id,
                order_id,
                amount,
                currency,
                provider,
                status,
                failure_code,
                processed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (payment_id) DO UPDATE SET
                amount = EXCLUDED.amount,
                provider = EXCLUDED.provider,
                status = EXCLUDED.status,
                failure_code = EXCLUDED.failure_code,
                processed_at = EXCLUDED.processed_at
            """,
            (
                payload.payment_id,
                payload.order_id,
                payload.amount,
                payload.currency,
                payload.provider,
                status,
                failure_code,
                event.occurred_at,
            ),
        )

    def _insert_inventory_adjustment(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: InventoryAdjustedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO inventory (
                inventory_event_id,
                product_id,
                quantity_delta,
                reason,
                adjusted_at
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (inventory_event_id) DO NOTHING
            """,
            (
                payload.inventory_event_id,
                payload.product_id,
                payload.quantity_delta,
                payload.reason,
                event.occurred_at,
            ),
        )

    def _upsert_shipment(
        self,
        connection: Connection[dict[str, object]],
        event: EcommerceEvent,
        payload: ShipmentCreatedPayload,
    ) -> None:
        connection.execute(
            """
            INSERT INTO shipments (
                shipment_id,
                order_id,
                carrier,
                tracking_number,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (shipment_id) DO UPDATE SET
                carrier = EXCLUDED.carrier,
                tracking_number = EXCLUDED.tracking_number,
                status = EXCLUDED.status
            """,
            (
                payload.shipment_id,
                payload.order_id,
                payload.carrier,
                payload.tracking_number,
                payload.status,
                event.occurred_at,
            ),
        )

    def _mark_shipment_delivered(
        self,
        connection: Connection[dict[str, object]],
        payload: ShipmentDeliveredPayload,
    ) -> None:
        connection.execute(
            """
            UPDATE shipments
            SET status = %s, delivered_at = %s
            WHERE shipment_id = %s
            """,
            (payload.status, payload.delivered_at, payload.shipment_id),
        )


def psycopg_connection_factory(database_url: str) -> ConnectionFactory:
    def connect() -> Connection[dict[str, object]]:
        return Connection.connect(database_url, row_factory=dict_row)

    return connect
