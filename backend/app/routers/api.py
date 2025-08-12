"""Main API endpoints for ReplyMint Backend"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime
import stripe
import boto3
from app.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.services.usage_tracker import get_usage_summary
from boto3.dynamodb.conditions import Key

router = APIRouter()
logger = logging.getLogger(__name__)


def _dynamodb_resource():
    settings = get_settings()
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def _get_settings_table():
    settings = get_settings()
    return _dynamodb_resource().Table(settings.settings_table)


@router.post("/stripe/create-checkout-session")
async def create_checkout_session(
    request_data: Dict[str, Any],
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Create a Stripe checkout session"""
    try:
        price_id = request_data.get("priceId")
        if not price_id:
            raise HTTPException(status_code=400, detail="priceId is required")

        # Get Stripe secret key from settings
        stripe_secret_key = settings.stripe_secret_key
        if not stripe_secret_key:
            logger.error("STRIPE_SECRET_KEY not configured")
            raise HTTPException(
                status_code=500, detail="Stripe not configured")

        # Initialize Stripe
        stripe.api_key = stripe_secret_key

        # Create checkout session
        session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url='https://replymint-staging.vercel.app/dashboard?checkout=success&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://replymint-staging.vercel.app/pricing?checkout=cancel',
            allow_promotion_codes=True,
        )

        logger.info(f"Created Stripe checkout session: {session.id}")

        return {
            "status": "success",
            "data": {
                "id": session.id,
                "url": session.url
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/dashboard/overview")
async def dashboard_overview(
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Get dashboard overview data"""
    try:
        # Get real user data from DynamoDB
        tenant_id = current_user["tenantId"]
        users_table = _dynamodb_resource().Table(settings.users_table)
        usage_table = _dynamodb_resource().Table(settings.usage_counters_table)

        # Get current month usage
        from datetime import datetime
        current_month = datetime.utcnow().strftime("%Y-%m")

        try:
            usage_response = usage_table.get_item(
                Key={"tenantId": tenant_id, "month": current_month}
            )
            current_usage = usage_response.get("Item", {}).get("count", 0)
        except Exception as e:
            logger.warning(f"Failed to get usage for {tenant_id}: {e}")
            current_usage = 0

        # Get user settings
        settings_table = _get_settings_table()
        try:
            user_settings = settings_table.get_item(
                Key={"tenantId": tenant_id}).get("Item", {})
        except Exception as e:
            logger.warning(f"Failed to get settings for {tenant_id}: {e}")
            user_settings = {}

        logger.info("Dashboard overview requested")

        return {
            "status": "success",
            "data": {
                "plan": {
                    "name": current_user.get("plan_tier", "starter").title(),
                    "monthly_limit": current_user.get("monthly_quota", 200),
                    "current_usage": current_usage,
                    "remaining": max(0, current_user.get("monthly_quota", 200) - current_usage)
                },
                "status": current_user.get("subscription_status", "trial"),
                "last_email": user_settings.get("last_email_processed"),
                "monthly_stats": {
                    "sent": current_usage,
                    "received": user_settings.get("emails_received", 0),
                    "success_rate": user_settings.get("success_rate", 0.0)
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/logs")
async def get_email_logs(
    limit: int = 50,
    offset: int = 0,
    tenantId: str | None = None,
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Get email logs with pagination. Optionally filter by tenantId (testing/admin)."""
    try:
        # Determine tenant to query
        tenant_id = tenantId or current_user["tenantId"]

        logs_table = _dynamodb_resource().Table(settings.email_logs_table)

        try:
            # Query logs for this tenant, sorted by timestamp (newest first)
            response = logs_table.query(
                KeyConditionExpression=Key("tenantId").eq(tenant_id),
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )

            logs = response.get("Items", [])
            # Apply offset if needed
            if offset > 0 and len(logs) > offset:
                logs = logs[offset:]

        except Exception as e:
            logger.warning(f"Failed to get logs for {tenant_id}: {e}")
            logs = []

        logger.info(
            f"Email logs requested: tenant={tenant_id}, limit={limit}, offset={offset}")

        return {
            "status": "success",
            "data": {
                "logs": logs,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(logs),
                    "has_more": len(logs) == limit
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error getting email logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/settings")
async def get_user_settings(
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Get user settings"""
    try:
        # Get real user settings from DynamoDB
        tenant_id = current_user["tenantId"]
        settings_table = _get_settings_table()

        try:
            response = settings_table.get_item(Key={"tenantId": tenant_id})
            user_settings = response.get("Item", {})
        except Exception as e:
            logger.warning(f"Failed to get settings for {tenant_id}: {e}")
            user_settings = {}

        # Return default settings if none exist
        if not user_settings:
            user_settings = {
                "tone": "professional",
                "max_length": 700,
                "signature": "",
                "auto_reply_enabled": True,
                "notifications": {
                    "email": True,
                    "slack": False
                }
            }

        logger.info("User settings requested")

        return {
            "status": "success",
            "data": user_settings,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error getting user settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/settings")
async def update_user_settings(
    settings_update: Dict[str, Any],
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Update user settings"""
    try:
        # Update real user settings in DynamoDB
        tenant_id = current_user["tenantId"]
        settings_table = _get_settings_table()

        # Validate required fields
        allowed_fields = {"tone", "max_length", "signature",
                          "auto_reply_enabled", "notifications"}
        filtered_update = {k: v for k,
                           v in settings_update.items() if k in allowed_fields}

        if not filtered_update:
            raise HTTPException(
                status_code=400, detail="No valid settings provided")

        # Add timestamp
        filtered_update["updated_at"] = int(datetime.utcnow().timestamp())

        try:
            # Use update_item to merge with existing settings
            update_expression = "SET " + \
                ", ".join([f"#{k} = :{k}" for k in filtered_update.keys()])
            expression_names = {f"#{k}": k for k in filtered_update.keys()}
            expression_values = {f":{k}": v for k,
                                 v in filtered_update.items()}

            settings_table.update_item(
                Key={"tenantId": tenant_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values
            )

        except Exception as e:
            logger.error(f"Failed to update settings for {tenant_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update settings")

        logger.info("User settings update requested", extra={
            "updated_fields": list(filtered_update.keys()),
            "tenant_id": tenant_id
        })

        return {
            "status": "success",
            "message": "Settings updated successfully",
            "updated_fields": list(filtered_update.keys()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api-key/generate")
async def generate_api_key(
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Generate new API key for user"""
    try:
        # Generate API key and store in user settings
        tenant_id = current_user["tenantId"]
        import secrets
        api_key = f"rm_{current_user.get('plan_tier', 'starter')}_{secrets.token_urlsafe(32)}"

        # Store API key in settings table
        settings_table = _get_settings_table()
        try:
            settings_table.update_item(
                Key={"tenantId": tenant_id},
                UpdateExpression="SET api_key = :key, api_key_created_at = :created",
                ExpressionAttributeValues={
                    ":key": api_key,
                    ":created": int(datetime.utcnow().timestamp())
                }
            )
        except Exception as e:
            logger.error(f"Failed to store API key for {tenant_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to generate API key")

        logger.info("API key generation requested")

        return {
            "status": "success",
            "data": {
                "api_key": api_key,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "expires_at": None
            },
            "message": "API key generated successfully. Store it securely - it won't be shown again."
        }

    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api-key/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Revoke API key"""
    try:
        # Revoke API key by removing it from settings
        tenant_id = current_user["tenantId"]
        settings_table = _get_settings_table()

        try:
            settings_table.update_item(
                Key={"tenantId": tenant_id},
                UpdateExpression="REMOVE api_key, api_key_created_at",
                ConditionExpression="tenantId = :tid"
            )
        except Exception as e:
            logger.error(f"Failed to revoke API key for {tenant_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to revoke API key")

        logger.info(f"API key revocation requested: {key_id}")

        return {
            "status": "success",
            "message": "API key revoked successfully",
            "deleted_key": key_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/usage/summary")
async def get_usage_summary_endpoint(
    current_user=Depends(get_current_user),
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Get detailed usage summary including quota warnings"""
    try:
        tenant_id = current_user["tenantId"]

        # Get comprehensive usage summary
        usage_data = get_usage_summary(tenant_id)

        logger.info("Usage summary requested", extra={
            "tenant_id": tenant_id,
            "warning_level": usage_data.get("warnings", {}).get("warning_level", "none")
        })

        return {
            "status": "success",
            "data": usage_data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
