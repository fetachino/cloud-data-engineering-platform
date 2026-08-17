"""Application factory for the local analytics API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.config import get_settings
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
    return application


app = create_app()
