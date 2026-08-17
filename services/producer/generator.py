from __future__ import annotations

import random
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

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

NAMESPACE = uuid.UUID("f8d016fd-dfb0-4e8c-a117-f6b506d7956e")


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int = 42
    event_count: int = 50
    producer_name: str = "synthetic-ecommerce-producer"
    start_time: datetime = datetime(2026, 1, 1, tzinfo=UTC)


class SyntheticEventGenerator:
    def __init__(self, config: GeneratorConfig) -> None:
        self.config = config
        self.random = random.Random(config.seed)
        self.generated_count = 0
        self.customers: list[uuid.UUID] = []
        self.products: list[uuid.UUID] = []
        self.orders: list[uuid.UUID] = []

    def generate(self) -> Iterator[EcommerceEvent]:
        while self.generated_count < self.config.event_count:
            if not self.customers:
                yield self._customer_created()
            elif len(self.products) < 4:
                yield self._product_created()
            else:
                yield from self._order_lifecycle()

    def _event_id(self, label: str) -> uuid.UUID:
        return uuid.uuid5(NAMESPACE, f"{self.config.seed}:{label}:{self.generated_count}")

    def _entity_id(self, label: str) -> uuid.UUID:
        return uuid.uuid5(NAMESPACE, f"{self.config.seed}:{label}")

    def _timestamp(self) -> datetime:
        return self.config.start_time + timedelta(seconds=self.generated_count * 7)

    def _event(
        self,
        event_type: EventType,
        correlation_id: uuid.UUID,
        payload: object,
    ) -> EcommerceEvent:
        if self.generated_count >= self.config.event_count:
            raise StopIteration
        event = EcommerceEvent.model_validate(
            {
                "event_id": self._event_id(event_type.value),
                "event_type": event_type,
                "event_version": 1,
                "occurred_at": self._timestamp(),
                "producer": self.config.producer_name,
                "correlation_id": correlation_id,
                "payload": payload,
            }
        )
        self.generated_count += 1
        return event

    def _customer_created(self) -> EcommerceEvent:
        index = len(self.customers) + 1
        customer_id = self._entity_id(f"customer:{index}")
        self.customers.append(customer_id)
        payload = CustomerCreatedPayload(
            customer_id=customer_id,
            email=f"customer{index:03d}@example.test",
            first_name=f"TestFirst{index}",
            last_name=f"TestLast{index}",
            country="US",
        )
        return self._event(EventType.CUSTOMER_CREATED, customer_id, payload)

    def _product_created(self) -> EcommerceEvent:
        index = len(self.products) + 1
        product_id = self._entity_id(f"product:{index}")
        self.products.append(product_id)
        categories = ["apparel", "home", "electronics", "outdoor"]
        payload = ProductCreatedPayload(
            product_id=product_id,
            sku=f"SKU-{index:04d}",
            name=f"Portfolio Product {index}",
            category=categories[(index - 1) % len(categories)],
            price=Decimal(f"{19 + index * 3}.99"),
        )
        return self._event(EventType.PRODUCT_CREATED, product_id, payload)

    def _order_lifecycle(self) -> Iterator[EcommerceEvent]:
        customer_id = self.random.choice(self.customers)
        order_number = len(self.orders) + 1
        order_id = self._entity_id(f"order:{order_number}")
        self.orders.append(order_id)
        correlation_id = order_id

        if self.generated_count >= self.config.event_count:
            return
        yield self._event(
            EventType.ORDER_CREATED,
            correlation_id,
            OrderCreatedPayload(
                order_id=order_id,
                customer_id=customer_id,
                status="created",
                currency="USD",
            ),
        )

        selected_products = self.random.sample(self.products, k=self.random.randint(1, 2))
        total = Decimal("0.00")
        for product_index, product_id in enumerate(selected_products, start=1):
            if self.generated_count >= self.config.event_count:
                return
            quantity = self.random.randint(1, 3)
            unit_price = Decimal(f"{20 + product_index * 4}.99")
            total += unit_price * quantity
            yield self._event(
                EventType.ORDER_ITEM_ADDED,
                correlation_id,
                OrderItemAddedPayload(
                    order_item_id=self._entity_id(f"order-item:{order_number}:{product_index}"),
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                ),
            )
            if self.generated_count >= self.config.event_count:
                return
            yield self._event(
                EventType.INVENTORY_ADJUSTED,
                correlation_id,
                InventoryAdjustedPayload(
                    inventory_event_id=self._entity_id(f"inventory:{order_number}:{product_index}"),
                    product_id=product_id,
                    quantity_delta=-quantity,
                    reason="order_reserved",
                ),
            )

        if self.generated_count >= self.config.event_count:
            return
        payment_id = self._entity_id(f"payment:{order_number}")
        payment_failed = self.random.random() < 0.15
        if payment_failed:
            yield self._event(
                EventType.PAYMENT_FAILED,
                correlation_id,
                PaymentFailedPayload(
                    payment_id=payment_id,
                    order_id=order_id,
                    amount=total,
                    currency="USD",
                    provider="stripe_test",
                    failure_code="card_declined",
                ),
            )
            return

        yield self._event(
            EventType.PAYMENT_COMPLETED,
            correlation_id,
            PaymentCompletedPayload(
                payment_id=payment_id,
                order_id=order_id,
                amount=total,
                currency="USD",
                provider="stripe_test",
            ),
        )

        if self.generated_count >= self.config.event_count:
            return
        shipment_id = self._entity_id(f"shipment:{order_number}")
        yield self._event(
            EventType.SHIPMENT_CREATED,
            correlation_id,
            ShipmentCreatedPayload(
                shipment_id=shipment_id,
                order_id=order_id,
                carrier="ups_test",
                tracking_number=f"1ZTEST{order_number:08d}",
                status="created",
            ),
        )
        if self.generated_count >= self.config.event_count:
            return
        yield self._event(
            EventType.SHIPMENT_DELIVERED,
            correlation_id,
            ShipmentDeliveredPayload(
                shipment_id=shipment_id,
                order_id=order_id,
                delivered_at=self._timestamp() + timedelta(days=3),
                status="delivered",
            ),
        )


def generate_events(config: GeneratorConfig) -> list[EcommerceEvent]:
    return list(SyntheticEventGenerator(config).generate())
