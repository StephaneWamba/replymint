"""Admin endpoints for ReplyMint Backend"""
from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

from app.dependencies.auth import get_current_user
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _dynamodb_resource():
    settings = get_settings()
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def _get_tables():
    settings = get_settings()
    ddb = _dynamodb_resource()
    return {
        "users": ddb.Table(settings.users_table),
        "usage": ddb.Table(settings.usage_counters_table),
        "logs": ddb.Table(settings.email_logs_table),
        "settings": ddb.Table(settings.settings_table)
    }


def _require_admin_role(current_user: Dict[str, Any]) -> None:
    """Check if current user has admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/admin/users")
async def list_users(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """List all users (admin only)"""
    _require_admin_role(current_user)

    try:
        tables = _get_tables()
        users_table = tables["users"]

        # Scan users table with pagination
        response = users_table.scan(
            Limit=limit,
            ExclusiveStartKey={"tenantId": "dummy"} if offset == 0 else None
        )

        users = response.get("Items", [])

        # Apply offset if needed
        if offset > 0 and len(users) > offset:
            users = users[offset:]

        # Get current month usage for each user
        current_month = datetime.utcnow().strftime("%Y-%m")
        usage_table = tables["usage"]

        for user in users:
            try:
                usage_response = usage_table.get_item(
                    Key={"tenantId": user["tenantId"], "month": current_month}
                )
                user["current_month_usage"] = usage_response.get(
                    "Item", {}).get("count", 0)
            except Exception as e:
                logger.warning(
                    f"Failed to get usage for {user['tenantId']}: {e}")
                user["current_month_usage"] = 0

        logger.info("Admin users list requested", extra={
            "admin_user": current_user["email"],
            "limit": limit,
            "offset": offset,
            "total_users": len(users)
        })

        return {
            "status": "success",
            "data": {
                "users": users,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(users),
                    "has_more": len(users) == limit
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/admin/stats")
async def system_statistics(
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Get system-wide statistics (admin only)"""
    _require_admin_role(current_user)

    try:
        tables = _get_tables()
        current_month = datetime.utcnow().strftime("%Y-%m")

        # Get total users
        users_table = tables["users"]
        users_response = users_table.scan(Select="COUNT")
        total_users = users_response.get("Count", 0)

        # Get active subscriptions
        active_users_response = users_table.scan(
            FilterExpression=Attr("subscription_status").eq("active")
        )
        active_subscriptions = len(active_users_response.get("Items", []))

        # Get current month total usage
        usage_table = tables["usage"]
        usage_response = usage_table.scan(
            FilterExpression=Key("month").eq(current_month)
        )
        current_month_usage = sum(
            item.get("count", 0) for item in usage_response.get("Items", [])
        )

        # Get plan distribution
        plan_distribution = {}
        for user in users_table.scan().get("Items", []):
            plan = user.get("plan_tier", "starter")
            plan_distribution[plan] = plan_distribution.get(plan, 0) + 1

        # Get recent email logs count
        logs_table = tables["logs"]
        logs_response = logs_table.scan(Select="COUNT")
        total_emails_processed = logs_response.get("Count", 0)

        logger.info("Admin system stats requested", extra={
            "admin_user": current_user["email"]
        })

        return {
            "status": "success",
            "data": {
                "users": {
                    "total": total_users,
                    "active_subscriptions": active_subscriptions,
                    "plan_distribution": plan_distribution
                },
                "usage": {
                    "current_month": current_month_usage,
                    "total_processed": total_emails_processed
                },
                "system": {
                    "environment": get_settings().environment,
                    "region": get_settings().aws_region
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/admin/users/{tenant_id}")
async def get_user_details(
    tenant_id: str,
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed user information (admin only)"""
    _require_admin_role(current_user)

    try:
        tables = _get_tables()
        users_table = tables["users"]

        # Get user details
        user_response = users_table.get_item(Key={"tenantId": tenant_id})
        if not user_response.get("Item"):
            raise HTTPException(status_code=404, detail="User not found")

        user = user_response["Item"]

        # Get user settings
        settings_table = tables["settings"]
        try:
            settings_response = settings_table.get_item(
                Key={"tenantId": tenant_id})
            user["settings"] = settings_response.get("Item", {})
        except Exception as e:
            logger.warning(f"Failed to get settings for {tenant_id}: {e}")
            user["settings"] = {}

        # Get usage history (last 6 months)
        usage_table = tables["usage"]
        usage_history = []

        for i in range(6):
            month = datetime.utcnow().replace(day=1)
            month = month.replace(month=month.month - i)
            month_key = month.strftime("%Y-%m")

            try:
                usage_response = usage_table.get_item(
                    Key={"tenantId": tenant_id, "month": month_key}
                )
                if usage_response.get("Item"):
                    usage_history.append({
                        "month": month_key,
                        "count": usage_response["Item"].get("count", 0)
                    })
            except Exception as e:
                logger.warning(
                    f"Failed to get usage for {tenant_id} {month_key}: {e}")

        # Get recent email logs
        logs_table = tables["logs"]
        try:
            logs_response = logs_table.query(
                KeyConditionExpression=Key("tenantId").eq(tenant_id),
                ScanIndexForward=False,
                Limit=10
            )
            user["recent_emails"] = logs_response.get("Items", [])
        except Exception as e:
            logger.warning(f"Failed to get logs for {tenant_id}: {e}")
            user["recent_emails"] = []

        logger.info("Admin user details requested", extra={
            "admin_user": current_user["email"],
            "target_user": tenant_id
        })

        return {
            "status": "success",
            "data": {
                "user": user,
                "usage_history": usage_history
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/admin/users/{tenant_id}")
async def update_user(
    tenant_id: str,
    updates: Dict[str, Any],
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Update user account (admin only)"""
    _require_admin_role(current_user)

    try:
        tables = _get_tables()
        users_table = tables["users"]

        # Check if user exists
        user_response = users_table.get_item(Key={"tenantId": tenant_id})
        if not user_response.get("Item"):
            raise HTTPException(status_code=404, detail="User not found")

        # Validate allowed fields
        allowed_fields = {
            "plan_tier", "monthly_quota", "subscription_status",
            "role", "auto_reply_enabled"
        }
        filtered_updates = {k: v for k,
                            v in updates.items() if k in allowed_fields}

        if not filtered_updates:
            raise HTTPException(
                status_code=400, detail="No valid fields to update")

        # Add timestamp
        filtered_updates["updated_at"] = int(datetime.utcnow().timestamp())

        # Update user
        update_expression = "SET " + \
            ", ".join([f"#{k} = :{k}" for k in filtered_updates.keys()])
        expression_names = {f"#{k}": k for k in filtered_updates.keys()}
        expression_values = {f":{k}": v for k, v in filtered_updates.items()}

        users_table.update_item(
            Key={"tenantId": tenant_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values
        )

        # If updating quota, reset current month usage
        if "monthly_quota" in filtered_updates:
            usage_table = tables["usage"]
            current_month = datetime.utcnow().strftime("%Y-%m")
            try:
                usage_table.update_item(
                    Key={"tenantId": tenant_id, "month": current_month},
                    UpdateExpression="SET #c = :zero",
                    ExpressionAttributeNames={"#c": "count"},
                    ExpressionAttributeValues={":zero": 0}
                )
            except Exception as e:
                logger.warning(f"Failed to reset usage for {tenant_id}: {e}")

        logger.info("Admin user update requested", extra={
            "admin_user": current_user["email"],
            "target_user": tenant_id,
            "updated_fields": list(filtered_updates.keys())
        })

        return {
            "status": "success",
            "message": "User updated successfully",
            "updated_fields": list(filtered_updates.keys()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/admin/users/{tenant_id}")
async def disable_user(
    tenant_id: str,
    current_user=Depends(get_current_user)
) -> Dict[str, Any]:
    """Disable user account (admin only)"""
    _require_admin_role(current_user)

    try:
        tables = _get_tables()
        users_table = tables["users"]

        # Check if user exists
        user_response = users_table.get_item(Key={"tenantId": tenant_id})
        if not user_response.get("Item"):
            raise HTTPException(status_code=404, detail="User not found")

        # Disable user
        users_table.update_item(
            Key={"tenantId": tenant_id},
            UpdateExpression="SET subscription_status = :status, updated_at = :updated",
            ExpressionAttributeValues={
                ":status": "disabled",
                ":updated": int(datetime.utcnow().timestamp())
            }
        )

        # Disable auto-reply in settings
        settings_table = tables["settings"]
        try:
            settings_table.update_item(
                Key={"tenantId": tenant_id},
                UpdateExpression="SET auto_reply_enabled = :disabled, updated_at = :updated",
                ExpressionAttributeValues={
                    ":disabled": False,
                    ":updated": int(datetime.utcnow().timestamp())
                }
            )
        except Exception as e:
            logger.warning(
                f"Failed to disable auto-reply for {tenant_id}: {e}")

        logger.info("Admin user disable requested", extra={
            "admin_user": current_user["email"],
            "target_user": tenant_id
        })

        return {
            "status": "success",
            "message": "User disabled successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
