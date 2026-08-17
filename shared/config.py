from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "ecommerce.events.v1"
    kafka_consumer_group: str = "ecommerce-ingestion-local"
    database_url: str = "postgresql://platform:platform@localhost:5432/ecommerce"
    consumer_metrics_port: int = 9101
