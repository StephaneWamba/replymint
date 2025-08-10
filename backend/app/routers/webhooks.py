"""Webhook endpoints for ReplyMint Backend"""
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
import logging
import hmac
import hashlib
from datetime import datetime

from ..core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/mailgun/inbound")
async def mailgun_inbound_webhook(
    request: Request,
    settings=Depends(get_settings)
) -> Dict[str, Any]:
    """Handle Mailgun inbound webhook"""
    try:
        # Verify webhook signature
        if not verify_mailgun_signature(request, settings):
            logger.warning("Invalid Mailgun webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse webhook payload
        form_data = await request.form()

        # Log the webhook
        logger.info("Received Mailgun inbound webhook", extra={
            "sender": form_data.get("from"),
            "recipient": form_data.get("to"),
            "subject": form_data.get("subject"),
            "message_id": form_data.get("Message-Id")
        })

        # TODO: Process email and generate AI reply (Epic 2)
        # For now, just acknowledge receipt

        return {
            "status": "received",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": "Webhook received, processing will be implemented in Epic 2"
        }

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
        # Verify webhook signature
        if not verify_mailgun_signature(request, settings):
            logger.warning("Invalid Mailgun events webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse webhook payload
        form_data = await request.form()

        # Log the event
        logger.info("Received Mailgun event webhook", extra={
            "event": form_data.get("event"),
            "message_id": form_data.get("Message-Id"),
            "recipient": form_data.get("recipient")
        })

        # TODO: Process delivery events (Epic 2)
        # For now, just acknowledge receipt

        return {
            "status": "received",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": "Event webhook received, processing will be implemented in Epic 2"
        }

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

        # TODO: Process Stripe events (Epic 3)
        # For now, just acknowledge receipt

        return {
            "status": "received",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": "Stripe webhook received, processing will be implemented in Epic 3"
        }

    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def verify_mailgun_signature(request: Request, settings) -> bool:
    """Verify Mailgun webhook signature"""
    # TODO: Implement proper signature verification (Epic 2)
    # For now, return True to allow development
    logger.info("Mailgun signature verification skipped (development mode)")
    return True


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
