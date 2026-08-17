"""Application factory for the local analytics API."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from psycopg import Error as PsycopgError
from psycopg import OperationalError

from services.api.config import get_settings
from services.api.middleware import observe_request
from services.api.routers import router


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Cloud Data Engineering Platform Analytics API",
        description="Read-only recruiter-facing metrics from the dbt analytics warehouse.",
        version="0.3.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )
    application.include_router(router)
    application.middleware("http")(observe_request)
    application.mount("/metrics", make_asgi_app())

    @application.exception_handler(OperationalError)
    async def database_error_handler(_request: Request, _error: OperationalError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "Warehouse unavailable"})

    @application.exception_handler(PsycopgError)
    async def database_query_error_handler(_request: Request, _error: PsycopgError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "Warehouse query unavailable"})

    return application


app = create_app()
