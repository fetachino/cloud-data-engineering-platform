from __future__ import annotations

import argparse
import json
import time
from typing import Any

from confluent_kafka import Producer

from services.producer.generator import GeneratorConfig, generate_events
from shared.config import Settings
from shared.logging import configure_logging, get_logger

logger = get_logger(__name__)


def delivery_report(error: object, message: Any) -> None:
    if error is not None:
        logger.error("event_delivery_failed", error=str(error))
        return
    logger.info(
        "event_delivered",
        topic=message.topic(),
        partition=message.partition(),
        offset=message.offset(),
    )


def run(event_count: int, rate_per_second: float, seed: int) -> None:
    settings = Settings()
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    delay = 0 if rate_per_second <= 0 else 1 / rate_per_second

    for event in generate_events(GeneratorConfig(seed=seed, event_count=event_count)):
        payload = event.model_dump_json()
        producer.produce(
            settings.kafka_topic,
            key=str(event.correlation_id),
            value=payload,
            callback=delivery_report,
        )
        producer.poll(0)
        logger.info(
            "event_produced",
            event_id=str(event.event_id),
            correlation_id=str(event.correlation_id),
            event_type=event.event_type.value,
        )
        if delay:
            time.sleep(delay)

    producer.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce deterministic e-commerce events to Kafka.",
    )
    parser.add_argument("--event-count", type=int, default=50)
    parser.add_argument("--rate-per-second", type=float, default=5)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()
    logger.info("producer_starting", cli_args=json.dumps(vars(args), sort_keys=True))
    run(args.event_count, args.rate_per_second, args.seed)


if __name__ == "__main__":
    main()
