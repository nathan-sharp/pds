"""Main Application Entrypoint for ARC Personal Data Server (PDS)."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    PdsException,
    generic_exception_handler,
    pds_exception_handler,
)
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # Initialize database tables on server startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Dispose connection pool on server shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    """Construct and configure FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Central authentication and blind data-synchronization server "
            "for ARC (Anthro Research Corporation) PDS zero-knowledge client suite."
        ),
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS) Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register custom and fail-closed exception handlers (ASVS V5)
    app.add_exception_handler(PdsException, pds_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Mount API V1 router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
