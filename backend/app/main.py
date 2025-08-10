from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import logging
from contextlib import asynccontextmanager

from .routers import health, webhooks, api
from .core.config import get_settings
from .core.logging import setup_logging

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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_origin_regex=settings.allowed_origin_regex,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Trusted host middleware (security)
    if settings.environment == "prod":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["replymint.vercel.app"]
        )

    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(api.router, prefix="/api/v1", tags=["api"])

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests"""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response

    return app


app = create_app()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
