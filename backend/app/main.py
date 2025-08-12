from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import logging
from contextlib import asynccontextmanager

from .routers import health, webhooks, api
from .routers import users as users_router
from .routers import admin as admin_router
from .core.config import get_settings
from .core.logging import setup_logging
from .core.security import setup_security_middleware, get_security_headers

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ReplyMint Backend")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")

    yield

    # Shutdown
    logger.info("Shutting down ReplyMint Backend")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()

    app = FastAPI(
        title="ReplyMint Backend",
        version="0.1.0",
        description="AI-powered email auto-reply service",
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "prod" else None,
        redoc_url="/redoc" if settings.environment != "prod" else None,
    )

    # Setup security middleware
    setup_security_middleware(app)

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(api.router, prefix="/api/v1", tags=["api"])
    app.include_router(users_router.router, prefix="/api/v1", tags=["users"])
    app.include_router(admin_router.router, prefix="/api/v1", tags=["admin"])

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests and add security headers"""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")

        # Add security headers
        for header, value in get_security_headers().items():
            response.headers[header] = value

        return response

    return app


app = create_app()

# The health endpoint is defined in `routers.health` and included via `include_router`.
