"""Low-cardinality Prometheus metrics for the API and ingestion consumer."""

from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

from prometheus_client import Counter, Gauge, Histogram
from psycopg import Error as PsycopgError

P = ParamSpec("P")
T = TypeVar("T")

API_REQUESTS = Counter(
    "platform_api_requests_total",
    "HTTP requests handled by the analytics API.",
    ("method", "route", "status"),
)
API_REQUEST_LATENCY = Histogram(
    "platform_api_request_duration_seconds",
    "Analytics API request latency in seconds.",
    ("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
API_IN_FLIGHT = Gauge(
    "platform_api_requests_in_flight",
    "Current number of in-flight analytics API requests.",
)
API_DATABASE_FAILURES = Counter(
    "platform_api_database_failures_total",
    "Warehouse connection or query failures observed by the analytics API.",
    ("operation",),
)
API_DATABASE_QUERY_LATENCY = Histogram(
    "platform_api_database_query_duration_seconds",
    "Analytics warehouse query latency in seconds.",
    ("operation",),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

CONSUMER_EVENTS_RECEIVED = Counter(
    "platform_consumer_events_received_total",
    "Kafka records handed to the ingestion processor.",
)
CONSUMER_EVENTS_PROCESSED = Counter(
    "platform_consumer_events_processed_total",
    "Events acknowledged by the ingestion processor.",
    ("result",),
)
CONSUMER_MALFORMED_EVENTS = Counter(
    "platform_consumer_malformed_events_total",
    "Malformed or schema-invalid Kafka events rejected by the processor.",
)
CONSUMER_PROCESSING_FAILURES = Counter(
    "platform_consumer_processing_failures_total",
    "Events that could not be safely acknowledged because processing failed.",
)
CONSUMER_DATABASE_FAILURES = Counter(
    "platform_consumer_database_failures_total",
    "Database failures encountered while processing events.",
)
CONSUMER_PROCESSING_DURATION = Histogram(
    "platform_consumer_event_processing_duration_seconds",
    "Event processing duration in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


def track_database_query(operation: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorate a bounded warehouse operation with latency and failure metrics."""

    def decorator(function: Callable[P, T]) -> Callable[P, T]:
        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            started = perf_counter()
            try:
                return function(*args, **kwargs)
            except PsycopgError:
                API_DATABASE_FAILURES.labels(operation=operation).inc()
                raise
            finally:
                API_DATABASE_QUERY_LATENCY.labels(operation=operation).observe(
                    perf_counter() - started
                )

        return wrapped

    return decorator
