"""Usage tracking and quota enforcement"""
from __future__ import annotations

from typing import Tuple, Dict, Any
from datetime import datetime
import logging
import boto3

from app.core.config import get_settings


logger = logging.getLogger(__name__)


def _tables():
    s = get_settings()
    ddb = boto3.resource("dynamodb", region_name=s.aws_region)
    return ddb.Table(s.usage_counters_table), ddb.Table(s.users_table)


def get_current_month_key(tenant_id: str) -> Tuple[str, str]:
    return tenant_id, datetime.utcnow().strftime("%Y-%m")


def increment_usage(tenant_id: str, amount: int = 1) -> int:
    usage_table, _ = _tables()
    tid, month = get_current_month_key(tenant_id)
    resp = usage_table.update_item(
        Key={"tenantId": tid, "month": month},
        UpdateExpression="SET #c = if_not_exists(#c, :zero) + :inc",
        ExpressionAttributeNames={"#c": "count"},
        ExpressionAttributeValues={":inc": amount, ":zero": 0},
        ReturnValues="UPDATED_NEW",
    )
    return int(resp["Attributes"]["count"])


def get_quota(tenant_id: str) -> int:
    _, users_table = _tables()
    user = users_table.get_item(Key={"tenantId": tenant_id}).get("Item") or {}
    return int(user.get("monthly_quota", 200))


def check_and_increment(tenant_id: str, amount: int = 1) -> Tuple[bool, int, int]:
    """Returns (allowed, new_count, quota)."""
    current = increment_usage(tenant_id, 0)  # ensure record exists
    quota = get_quota(tenant_id)
    if current + amount > quota:
        logger.info("Quota exceeded", extra={
                    "tenant_id": tenant_id, "current": current, "quota": quota})
        return False, current, quota
    new_count = increment_usage(tenant_id, amount)
    return True, new_count, quota


def check_quota_warnings(tenant_id: str) -> Dict[str, Any]:
    """Check if user is approaching quota limits and return warning status"""
    try:
        usage_table, users_table = _tables()
        current_month = datetime.utcnow().strftime("%Y-%m")

        # Get current usage
        usage_response = usage_table.get_item(
            Key={"tenantId": tenant_id, "month": current_month}
        )
        current_usage = usage_response.get("Item", {}).get("count", 0)

        # Get user quota
        user = users_table.get_item(
            Key={"tenantId": tenant_id}).get("Item") or {}
        quota = int(user.get("monthly_quota", 200))

        # Calculate percentages
        usage_percentage = (current_usage / quota) * 100 if quota > 0 else 0

        # Determine warning level
        warning_level = "none"
        if usage_percentage >= 100:
            warning_level = "exceeded"
        elif usage_percentage >= 90:
            warning_level = "critical"
        elif usage_percentage >= 80:
            warning_level = "warning"
        elif usage_percentage >= 60:
            warning_level = "notice"

        # Generate warning messages
        warnings = []
        if warning_level == "exceeded":
            warnings.append(
                f"Monthly quota exceeded! You've used {current_usage}/{quota} emails.")
        elif warning_level == "critical":
            warnings.append(
                f"Critical: You're at {usage_percentage:.1f}% of your monthly quota ({current_usage}/{quota}).")
        elif warning_level == "warning":
            warnings.append(
                f"Warning: You're at {usage_percentage:.1f}% of your monthly quota ({current_usage}/{quota}).")
        elif warning_level == "notice":
            warnings.append(
                f"Notice: You've used {usage_percentage:.1f}% of your monthly quota ({current_usage}/{quota}).")

        logger.info("Quota warning check", extra={
            "tenant_id": tenant_id,
            "current_usage": current_usage,
            "quota": quota,
            "usage_percentage": usage_percentage,
            "warning_level": warning_level
        })

        return {
            "warning_level": warning_level,
            "usage_percentage": usage_percentage,
            "current_usage": current_usage,
            "quota": quota,
            "remaining": max(0, quota - current_usage),
            "warnings": warnings,
            "is_critical": warning_level in ["critical", "exceeded"]
        }

    except Exception as e:
        logger.error(f"Error checking quota warnings for {tenant_id}: {e}")
        return {
            "warning_level": "error",
            "usage_percentage": 0,
            "current_usage": 0,
            "quota": 0,
            "remaining": 0,
            "warnings": ["Error checking quota status"],
            "is_critical": False
        }


def get_usage_summary(tenant_id: str) -> Dict[str, Any]:
    """Get comprehensive usage summary including warnings"""
    try:
        # Get basic usage info
        allowed, current_count, quota = check_and_increment(tenant_id, 0)

        # Get quota warnings
        warning_info = check_quota_warnings(tenant_id)

        # Get usage history (last 3 months)
        usage_table, _ = _tables()
        usage_history = []

        for i in range(3):
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

        return {
            "current_month": {
                "usage": current_count,
                "quota": quota,
                "remaining": max(0, quota - current_count),
                "percentage": (current_count / quota) * 100 if quota > 0 else 0
            },
            "warnings": warning_info,
            "history": usage_history,
            "status": "active" if allowed else "quota_exceeded"
        }

    except Exception as e:
        logger.error(f"Error getting usage summary for {tenant_id}: {e}")
        return {
            "current_month": {"usage": 0, "quota": 0, "remaining": 0, "percentage": 0},
            "warnings": {"warning_level": "error", "warnings": ["Error retrieving usage data"]},
            "history": [],
            "status": "error"
        }
