from __future__ import annotations

from confluent_kafka import Consumer, KafkaException
from prometheus_client import start_http_server

from services.consumer.processor import EventProcessor
from services.consumer.repository import EventRepository, psycopg_connection_factory
from shared.config import Settings
from shared.logging import configure_logging, get_logger

logger = get_logger(__name__)


def run() -> None:
    settings = Settings()
    start_http_server(settings.consumer_metrics_port, addr="0.0.0.0")
    logger.info("consumer_metrics_started", port=settings.consumer_metrics_port)
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_consumer_group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    processor = EventProcessor(EventRepository(psycopg_connection_factory(settings.database_url)))
    consumer.subscribe([settings.kafka_topic])
    logger.info("consumer_started", topic=settings.kafka_topic, group=settings.kafka_consumer_group)

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                raise KafkaException(message.error())
            value = message.value()
            if value is None:
                logger.warning("empty_kafka_message_rejected")
                consumer.commit(message=message, asynchronous=False)
                continue
            result = processor.process_message(value)
            if result.acknowledged:
                consumer.commit(message=message, asynchronous=False)
    finally:
        consumer.close()


def main() -> None:
    configure_logging()
    run()


if __name__ == "__main__":
    main()
