"""Email processing pipeline: parse inbound, generate reply, log and send."""
from __future__ import annotations

from typing import Dict, Any
from datetime import datetime
import logging
import boto3
import httpx
import asyncio

from app.core.config import get_settings
from app.services.ai_service import generate_reply
from app.services.usage_tracker import check_and_increment


logger = logging.getLogger(__name__)


def _ddb():
    s = get_settings()
    return boto3.resource("dynamodb", region_name=s.aws_region)


def _tables():
    s = get_settings()
    d = _ddb()
    return d.Table(s.email_logs_table), d.Table(s.users_table)


def process_inbound_email(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process inbound Mailgun webhook form data and return reply content."""
    settings = get_settings()

    sender = form_data.get("from", "")
    recipient = form_data.get("recipient") or form_data.get("to") or ""
    subject = form_data.get("subject", "")
    body_plain = form_data.get(
        "body-plain") or form_data.get("stripped-text") or ""

    # Derive tenant from recipient alias or map by domain; for now, use recipient email
    tenant_id = recipient.lower()

    # Get user context for tone/signature
    _, users_table = _tables()
    user = users_table.get_item(Key={"tenantId": tenant_id}).get("Item") or {}
    context = {
        "tone": "professional",
        "signature": user.get("signature", ""),
    }

    # Quota check
    allowed, new_count, quota = check_and_increment(tenant_id, 1)
    if not allowed:
        logger.info("Reply suppressed due to quota",
                    extra={"tenant": tenant_id})
        reply_text = ""
        status = "quota_exceeded"
    else:
        email = {"from": sender, "to": recipient, "subject": subject,
                 "body": body_plain, "context": context}
        try:
            reply_text = generate_reply(email)
            status = "generated"
        except Exception:
            logger.warning(
                "AI unavailable or failed; returning explicit fallback", exc_info=True)
            reply_text = "AI is currently unavailable, so no automatic reply was generated."
            status = "ai_unavailable"

    # Log email
    logs_table, _ = _tables()
    now_iso = datetime.utcnow().isoformat() + "Z"
    log_item = {
        "tenantId": tenant_id,
        "timestamp": now_iso,
        "direction": "inbound",
        "from": sender,
        "to": recipient,
        "subject": subject,
        "status": status,
        "reply_preview": reply_text[:256],
        "ai_tokens_used": 100,  # Mock value for now
        "cost": 0.002,  # Mock value for now
    }
    try:
        logs_table.put_item(Item=log_item)
        logger.info("Email logged successfully", extra={
                    "tenant_id": tenant_id, "status": status})
    except Exception as e:
        logger.error("Failed to log inbound email", extra={
                     "error": str(e), "tenant_id": tenant_id}, exc_info=True)

    return {
        "tenant_id": tenant_id,
        "status": status,
        "reply": reply_text,
        "usage": {"count": new_count, "quota": quota},
    }


async def send_outbound_email(
    to_email: str,
    from_email: str,
    subject: str,
    body: str,
    tenant_id: str,
    timeout: int = 10
) -> Dict[str, Any]:
    """Send outbound email via Mailgun API"""
    settings = get_settings()

    logger.info("Starting outbound email send", extra={
        "to": to_email,
        "from": from_email,
        "tenant_id": tenant_id,
        "has_api_key": bool(settings.mailgun_api_key),
        "has_domain": bool(settings.mailgun_domain_outbound)
    })

    if not settings.mailgun_api_key or not settings.mailgun_domain_outbound:
        logger.warning("Mailgun outbound not configured")
        return {"status": "error", "message": "Mailgun outbound not configured"}

    # Prepare email data
    email_data = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "text": body,
    }

    logger.info("Prepared email data", extra={
        "email_data": email_data,
        "api_url": f"https://api.mailgun.net/v3/{settings.mailgun_domain_outbound}/messages"
    })

    # Send via Mailgun API
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info("Sending request to Mailgun API")
            response = await client.post(
                f"https://api.mailgun.net/v3/{settings.mailgun_domain_outbound}/messages",
                auth=("api", settings.mailgun_api_key),
                data=email_data
            )

            logger.info("Received response from Mailgun", extra={
                "status_code": response.status_code,
                "response_headers": dict(response.headers)
            })

            if response.status_code == 200:
                logger.info("Outbound email sent successfully", extra={
                    "to": to_email,
                    "tenant_id": tenant_id
                })

                # Log successful outbound
                logs_table, _ = _tables()
                now_iso = datetime.utcnow().isoformat() + "Z"
                log_item = {
                    "tenantId": tenant_id,
                    "timestamp": now_iso,
                    "direction": "outbound",
                    "from": from_email,
                    "to": to_email,
                    "subject": subject,
                    "status": "sent",
                    "mailgun_id": response.json().get("id", ""),
                }

                try:
                    logs_table.put_item(Item=log_item)
                except Exception:
                    logger.warning(
                        "Failed to log outbound email", exc_info=True)

                return {"status": "sent", "mailgun_id": response.json().get("id", "")}
            else:
                logger.error("Mailgun API error", extra={
                    "status_code": response.status_code,
                    "response": response.text,
                    "response_headers": dict(response.headers)
                })
                return {"status": "error", "message": f"Mailgun API error: {response.status_code}"}

    except asyncio.TimeoutError:
        logger.error("Mailgun API timeout", extra={"timeout": timeout})
        return {"status": "error", "message": "Mailgun API timeout"}
    except Exception as e:
        logger.error("Failed to send outbound email", extra={
                     "error": str(e), "error_type": type(e).__name__}, exc_info=True)
        return {"status": "error", "message": f"Send failed: {str(e)}"}
