"""User and authentication endpoints"""
from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import logging

from app.core.config import get_settings
from app.services.auth_service import generate_jwt, get_or_create_user, create_admin_user
from app.dependencies.auth import get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/users/login")
async def login_user(payload: Dict[str, Any], settings=Depends(get_settings)) -> Dict[str, Any]:
    """Temporary login endpoint to exchange email for backend JWT.

    In production this will be called by the frontend after magic-link verification.
    """
    email = (payload.get("email") or "").strip().lower()
    name = (payload.get("name") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    user = get_or_create_user(email, name=name or None)
    token = generate_jwt(
        {"email": user["email"], "tenantId": user["tenantId"], "role": user.get("role", "user")})

    return {
        "status": "success",
        "token": token,
        "user": {
            "email": user["email"],
            "tenantId": user["tenantId"],
            "plan_tier": user.get("plan_tier"),
            "subscription_status": user.get("subscription_status"),
            "role": user.get("role", "user"),
        },
    }


@router.get("/users/profile")
async def get_profile(current_user=Depends(get_current_user)) -> Dict[str, Any]:
    return {"status": "success", "user": current_user}


@router.post("/users/admin/create")
async def create_admin_account(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Create an admin user account (requires existing user)"""
    # For now, allow any authenticated user to create admin accounts
    # In production, you might want to restrict this to existing admins

    email = (payload.get("email") or "").strip().lower()
    name = (payload.get("name") or "").strip()

    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    # Create admin user
    admin_user = create_admin_user(email, name=name or None)

    # Generate JWT for the new admin
    token = generate_jwt({
        "email": admin_user["email"],
        "tenantId": admin_user["tenantId"],
        "role": admin_user["role"]
    })

    logger.info(f"Admin user created by {current_user['email']}: {email}")

    return {
        "status": "success",
        "message": "Admin user created successfully",
        "token": token,
        "user": {
            "email": admin_user["email"],
            "tenantId": admin_user["tenantId"],
            "role": admin_user["role"],
            "plan_tier": admin_user.get("plan_tier"),
            "subscription_status": admin_user.get("subscription_status"),
        },
    }
