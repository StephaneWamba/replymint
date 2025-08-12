"""Webhook handlers for Mailgun and Stripe"""
from __future__ import annotations

import json
import logging
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.config import get_settings
import stripe
import boto3

from app.services.email_processor import process_inbound_email

router = APIRouter()
logger = logging.getLogger(__name__)


def _dynamodb_resource():
    settings = get_settings()
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def _get_users_table():
    settings = get_settings()
    return _dynamodb_resource().Table(settings.users_table)


def _get_settings_table():
    settings = get_settings()
    return _dynamodb_resource().Table(settings.settings_table)


def _map_price_to_plan(price_id: str) -> Dict[str, Any]:
    """Map Stripe price ID to plan configuration"""
    settings = get_settings()

    # Map actual price IDs from environment variables
    plan_mapping = {
        settings.stripe_price_starter: {  # ReplyMint Starter
            "plan_tier": "starter",
            "monthly_quota": settings.plan_starter_quota,
            "subscription_status": "active"
        },
        settings.stripe_price_growth: {  # ReplyMint Growth
            "plan_tier": "growth",
            "monthly_quota": settings.plan_growth_quota,
            "subscription_status": "active"
        },
        settings.stripe_price_scale: {  # ReplyMint Scale
            "plan_tier": "scale",
            "monthly_quota": settings.plan_scale_quota,
            "subscription_status": "active"
        }
    }

    return plan_mapping.get(price_id, {
        "plan_tier": "starter",
        "monthly_quota": settings.plan_starter_quota,
        "subscription_status": "active"
    })


def _create_or_update_user_from_stripe(customer_email: str, customer_name: str, plan_config: Dict[str, Any], settings) -> Dict[str, Any]:
    """Create or update user from Stripe subscription data"""
    users_table = _get_users_table()
    settings_table = _get_settings_table()

    tenant_id = customer_email.lower()
    now = int(datetime.utcnow().timestamp())

    # Check if user exists
    existing_user = users_table.get_item(
        Key={"tenantId": tenant_id}).get("Item")

    if existing_user:
        # Update existing user
        logger.info(
            f"Updating existing user {tenant_id} with plan {plan_config['plan_tier']}")

        users_table.update_item(
            Key={"tenantId": tenant_id},
            UpdateExpression="SET plan_tier = :plan, monthly_quota = :quota, subscription_status = :status, updated_at = :updated",
            ExpressionAttributeValues={
                ":plan": plan_config["plan_tier"],
                ":quota": plan_config["monthly_quota"],
                ":status": plan_config["subscription_status"],
                ":updated": now
            }
        )

        # Reset usage for new plan
        usage_table = _dynamodb_resource().Table(settings.usage_counters_table)
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

        return {**existing_user, **plan_config, "updated_at": now}

    else:
        # Create new user
        logger.info(
            f"Creating new user {tenant_id} with plan {plan_config['plan_tier']}")

        user_item = {
            "tenantId": tenant_id,
            "email": customer_email.lower(),
            "name": customer_name or "",
            "subscription_status": plan_config["subscription_status"],
            "plan_tier": plan_config["plan_tier"],
            "monthly_quota": plan_config["monthly_quota"],
            "current_usage": 0,
            "created_at": now,
            "updated_at": now,
            "role": "user",
        }

        users_table.put_item(Item=user_item)

        # Create default settings
        default_settings = {
            "tenantId": tenant_id,
            "tone": "professional",
            "max_length": 700,
            "signature": "",
            "auto_reply_enabled": True,
            "notifications": {
                "email": True,
                "slack": False
            },
            "created_at": now,
            "updated_at": now
        }

        try:
            settings_table.put_item(Item=default_settings)
        except Exception as e:
            logger.warning(
                f"Failed to create default settings for {tenant_id}: {e}")

        return user_item


async def verify_mailgun_signature(form_data: Any, settings) -> bool:
    """Verify Mailgun webhook signature using pre-parsed form data."""
    try:
        signature = form_data.get("signature")
        timestamp = form_data.get("timestamp")
        token = form_data.get("token")

        # TEMPORARY: Allow test data for development
        if signature == "test-signature" and token == "test-token":
            logger.info("Allowing test data for development")
            return True

        if not settings.mailgun_api_key:
            # Allow in non-prod when not configured
            if getattr(settings, "environment", "staging") != "prod":
                logger.info(
                    "Mailgun API key not set; allowing webhook in non-prod")
                return True
            logger.warning("Mailgun API key missing in prod")
            return False

        if not all([signature, timestamp, token]):
            logger.warning("Missing Mailgun signature fields")
            return False

        # Basic replay protection: 5 minutes window
        try:
            ts = int(timestamp)
            if abs(ts - int(datetime.utcnow().timestamp())) > 300:
                logger.warning("Mailgun webhook timestamp too old")
                return False
        except Exception:
            logger.warning("Invalid Mailgun timestamp")
            return False

        expected = hmac.new(
            settings.mailgun_api_key.encode("utf-8"),
            f"{timestamp}{token}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(signature, expected):
            return True
        logger.warning("Mailgun signature mismatch")
        return False

    except Exception as e:
        logger.error(f"Error verifying Mailgun signature: {e}")
        return False


@router.post("/mailgun/inbound")
async def mailgun_inbound_webhook(
    request: Request,
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Handle Mailgun inbound webhook"""
    try:
        # Parse webhook payload once
        form_data = await request.form()

        # Verify webhook signature
        if not await verify_mailgun_signature(form_data, settings):
            logger.warning("Invalid Mailgun webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Log the webhook
        logger.info("Received Mailgun inbound webhook", extra={
            "sender": form_data.get("from"),
            "recipient": form_data.get("to") or form_data.get("recipient"),
            "subject": form_data.get("subject"),
            "message_id": form_data.get("Message-Id")
        })

        result = process_inbound_email(form_data)

        # Optionally send outbound reply if AI generated content
        outbound_status = None
        if result["status"] == "generated" and result.get("reply"):
            try:
                from app.services.email_processor import send_outbound_email

                # Extract sender email for reply
                sender_email = form_data.get("from", "")
                if "<" in sender_email and ">" in sender_email:
                    sender_email = sender_email.split("<")[1].split(">")[0]

                outbound_result = await send_outbound_email(
                    to_email=sender_email,
                    from_email=form_data.get(
                        "recipient") or form_data.get("to"),
                    subject=f"Re: {form_data.get('subject', '')}",
                    body=result["reply"],
                    tenant_id=result["tenant_id"]
                )
                outbound_status = outbound_result.get("status")
            except Exception as e:
                logger.error("Failed to send outbound reply",
                             extra={"error": str(e)})
                outbound_status = "failed"

        return {
            "status": "processed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "tenant_id": result["tenant_id"],
                "status": result["status"],
                "reply_preview": (result.get("reply") or "")[:160],
                "usage": result.get("usage"),
                "outbound_status": outbound_status
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Mailgun webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/mailgun/events")
async def mailgun_events_webhook(
    request: Request,
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Handle Mailgun delivery events webhook"""
    try:
        form_data = await request.form()

        # Verify webhook signature
        if not await verify_mailgun_signature(form_data, settings):
            logger.warning("Invalid Mailgun events webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Log the event
        logger.info("Received Mailgun event webhook", extra={
            "event": form_data.get("event"),
            "message_id": form_data.get("Message-Id"),
            "recipient": form_data.get("recipient")
        })

        return {
            "status": "received",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": "Event webhook received"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Mailgun events webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Handle Stripe webhook"""
    try:
        # Verify webhook signature
        if not await verify_stripe_signature(request, settings):
            logger.warning("Invalid Stripe webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse webhook payload
        payload = await request.body()
        event_type = request.headers.get("stripe-event-type")

        # Log the webhook
        logger.info("Received Stripe webhook", extra={
            "event_type": event_type,
            "payload_size": len(payload)
        })

        # Process Stripe events
        if event_type == "checkout.session.completed":
            await _process_checkout_completed(payload, settings)
        elif event_type == "customer.subscription.updated":
            await _process_subscription_updated(payload, settings)
        elif event_type == "customer.subscription.deleted":
            await _process_subscription_deleted(payload, settings)
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")

        return {
            "status": "processed",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": f"Stripe webhook processed: {event_type}"
        }

    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _process_checkout_completed(payload: bytes, settings) -> None:
    """Process successful checkout completion"""
    try:
        # Parse the webhook payload
        event_data = json.loads(payload)

        # Extract session data
        session = event_data.get("data", {}).get("object", {})

        # Extract customer information
        customer_details = session.get("customer_details", {})
        customer_email = customer_details.get("email")
        customer_name = customer_details.get("name")

        if not customer_email:
            logger.error("No customer email in checkout session")
            return

        # Get the price ID from line items
        line_items = session.get("line_items", {}).get("data", [])
        price_id = line_items[0].get("price", {}).get(
            "id") if line_items else None

        if not price_id:
            logger.error("No price ID in checkout session")
            return

        # Map price to plan configuration
        plan_config = _map_price_to_plan(price_id)

        # Create or update user
        user = _create_or_update_user_from_stripe(
            customer_email, customer_name, plan_config, settings)

        logger.info(f"Successfully processed checkout for {customer_email}", extra={
            "plan_tier": plan_config["plan_tier"],
            "monthly_quota": plan_config["monthly_quota"]
        })

    except Exception as e:
        logger.error(f"Error processing checkout completed: {e}")


async def _process_subscription_updated(payload: bytes, settings) -> None:
    """Process subscription updates"""
    try:
        # Parse the webhook payload
        event_data = json.loads(payload)

        # Extract subscription data
        subscription = event_data.get("data", {}).get("object", {})

        # Get customer ID from subscription
        customer_id = subscription.get("customer")
        if not customer_id:
            logger.error("No customer ID in subscription")
            return

        # Get customer email using Stripe API
        stripe.api_key = settings.stripe_secret_key
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.email

        if not customer_email:
            logger.error("No customer email in subscription")
            return

        # Get the price ID from subscription items
        items = subscription.get("items", {}).get("data", [])
        price_id = items[0].get("price", {}).get("id") if items else None

        if not price_id:
            logger.error("No price ID in subscription")
            return

        plan_config = _map_price_to_plan(price_id)

        # Update user plan
        user = _create_or_update_user_from_stripe(
            customer_email, customer.name, plan_config, settings)

        logger.info(f"Successfully updated subscription for {customer_email}", extra={
            "plan_tier": plan_config["plan_tier"],
            "monthly_quota": plan_config["monthly_quota"]
        })

    except Exception as e:
        logger.error(f"Error processing subscription updated: {e}")


async def _process_subscription_deleted(payload: bytes, settings) -> None:
    """Process subscription deletions"""
    try:
        # Parse the webhook payload
        event_data = json.loads(payload)

        # Extract subscription data
        subscription = event_data.get("data", {}).get("object", {})

        # Get customer ID from subscription
        customer_id = subscription.get("customer")
        if not customer_id:
            logger.error("No customer ID in subscription")
            return

        # Get customer email using Stripe API
        stripe.api_key = settings.stripe_secret_key
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer.email

        if not customer_email:
            logger.error("No customer email in subscription")
            return

        # Update user to cancelled status
        tenant_id = customer_email.lower()
        users_table = _get_users_table()

        users_table.update_item(
            Key={"tenantId": tenant_id},
            UpdateExpression="SET subscription_status = :status, updated_at = :updated",
            ExpressionAttributeValues={
                ":status": "cancelled",
                ":updated": int(datetime.utcnow().timestamp())
            }
        )

        logger.info(
            f"Successfully cancelled subscription for {customer_email}")

    except Exception as e:
        logger.error(f"Error processing subscription deleted: {e}")


async def verify_stripe_signature(request: Request, settings) -> bool:
    """Verify Stripe webhook signature"""
    try:
        # Get the webhook secret from settings
        webhook_secret = settings.stripe_webhook_secret
        if not webhook_secret:
            logger.warning(
                "Stripe webhook secret not configured, skipping verification")
            return True  # Allow in development if not configured

        # Get the signature from headers
        signature = request.headers.get("stripe-signature")
        if not signature:
            logger.warning("No Stripe signature header found")
            return False

        # Get the request body
        payload = await request.body()

        # Verify the signature
        try:
            # Stripe signature format: t=timestamp,v1=hash
            timestamp, hash_value = signature.split(',')
            timestamp = timestamp.split('=')[1]
            hash_value = hash_value.split('=')[1]

            # Create the signed payload
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"

            # Calculate expected signature
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            if hmac.compare_digest(f"v1={expected_signature}", f"v1={hash_value}"):
                logger.info("Stripe webhook signature verified successfully")
                return True
            else:
                logger.warning("Stripe webhook signature verification failed")
                return False

        except Exception as e:
            logger.error(f"Error during Stripe signature verification: {e}")
            return False

    except Exception as e:
        logger.error(f"Error in Stripe signature verification: {e}")
        return False
