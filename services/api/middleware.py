"""Request metrics and structured request logging for FastAPI."""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response

from services.observability.metrics import API_IN_FLIGHT, API_REQUEST_LATENCY, API_REQUESTS
from shared.logging import get_logger

logger = get_logger(__name__)

_KNOWN_ROUTE_PATHS = {
    "/health",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/api/v1/analytics/overview",
    "/api/v1/analytics/orders",
    "/api/v1/analytics/products",
    "/api/v1/analytics/customers",
    "/api/v1/analytics/payments",
    "/api/v1/analytics/shipments",
}


def _route_name(request: Request) -> str:
    """Return a bounded route label without exposing arbitrary URL paths."""

    path = request.url.path.rstrip("/") or "/"
    return path if path in _KNOWN_ROUTE_PATHS else "unmatched"


async def observe_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Record bounded route metrics and attach a traceable request identifier."""

    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    started = perf_counter()
    API_IN_FLIGHT.inc()
    response: Response | None = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration = perf_counter() - started
        route_name = _route_name(request)
        status = str(response.status_code if response is not None else 500)
        API_REQUESTS.labels(request.method, route_name, status).inc()
        API_REQUEST_LATENCY.labels(request.method, route_name).observe(duration)
        API_IN_FLIGHT.dec()
        logger.info(
            "api_request_completed",
            request_id=request_id,
            method=request.method,
            route=route_name,
            status_code=status,
            duration_ms=round(duration * 1000, 2),
        )
        if response is not None:
            response.headers["X-Request-ID"] = request_id
