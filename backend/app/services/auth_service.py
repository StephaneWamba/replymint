"""Authentication service: JWT handling and basic user management"""
from __future__ import annotations

import os
import time
import logging
from typing import Dict, Any, Optional

import boto3
import jwt

from app.core.config import get_settings


logger = logging.getLogger(__name__)


def _get_tables() -> Dict[str, str]:
    settings = get_settings()
    return {
        "users": settings.users_table,
    }


def _dynamodb_resource():
    settings = get_settings()
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def generate_jwt(payload: Dict[str, Any], expires_minutes: int = 60) -> str:
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT secret not configured")

    now = int(time.time())
    claims = {
        **payload,
        "iat": now,
        "exp": now + expires_minutes * 60,
        "iss": "replymint",
        "aud": "replymint-app",
    }
    token = jwt.encode(claims, settings.jwt_secret, algorithm="HS256")
    # PyJWT returns str on py3
    return token


def verify_jwt(token: str) -> Dict[str, Any]:
    settings = get_settings()
    decoded = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        audience="replymint-app",
        issuer="replymint",
    )
    return decoded


def get_or_create_user(email: str, name: Optional[str] = None, role: str = "user") -> Dict[str, Any]:
    """Idempotently create a minimal user profile keyed by email."""
    tables = _get_tables()
    table = _dynamodb_resource().Table(tables["users"])

    # Use email as tenantId for now
    tenant_id = email.lower()

    # Try to fetch existing
    existing = table.get_item(Key={"tenantId": tenant_id}).get("Item")
    if existing:
        # Update role if it's different and user is requesting admin
        if role == "admin" and existing.get("role") != "admin":
            table.update_item(
                Key={"tenantId": tenant_id},
                UpdateExpression="SET #r = :role, updated_at = :updated",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={
                    ":role": role,
                    ":updated": int(time.time())
                }
            )
            existing["role"] = role
            logger.info(f"Updated user {tenant_id} to admin role")
        return existing

    item = {
        "tenantId": tenant_id,
        "email": email.lower(),
        "name": name or "",
        "subscription_status": "trial",
        "plan_tier": "starter",
        "monthly_quota": 200,
        "current_usage": 0,
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "role": role,
    }
    table.put_item(Item=item)

    if role == "admin":
        logger.info(f"Created admin user: {tenant_id}")
    else:
        logger.info(f"Created user: {tenant_id}")

    return item


def create_admin_user(email: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Create an admin user with elevated privileges"""
    return get_or_create_user(email, name, role="admin")


def get_user(email: str) -> Optional[Dict[str, Any]]:
    tables = _get_tables()
    table = _dynamodb_resource().Table(tables["users"])
    tenant_id = email.lower()
    return table.get_item(Key={"tenantId": tenant_id}).get("Item")


def is_admin(email: str) -> bool:
    """Check if user has admin role"""
    user = get_user(email)
    return user is not None and user.get("role") == "admin"
