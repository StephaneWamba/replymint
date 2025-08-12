"""Security configuration for ReplyMint Backend"""
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import get_settings


def setup_security_middleware(app: FastAPI) -> None:
    """Configure security middleware for the FastAPI application"""
    settings = get_settings()

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins or [
            "https://replymint-staging.vercel.app",
            "https://replymint.vercel.app"
        ],
        allow_origin_regex=settings.allowed_origin_regex,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key", "Authorization"],
        max_age=300,
    )

    # Trusted host middleware (for production)
    if settings.environment == "prod":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[
                "replymint.vercel.app",
                "*.vercel.app",
                "localhost",
                "127.0.0.1"
            ]
        )


def get_security_headers() -> dict:
    """Get security headers to be added to responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
