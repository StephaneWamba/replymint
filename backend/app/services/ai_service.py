"""AI Service for generating email replies using GPT-4o Mini"""
from __future__ import annotations

from typing import Dict, Any
import logging

from openai import OpenAI
from app.core.config import get_settings


logger = logging.getLogger(__name__)


def _client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=settings.openai_api_key)


def build_prompt(email: Dict[str, Any]) -> str:
    subject = email.get("subject", "")
    body = email.get("body", "")
    sender = email.get("from", "")
    context = email.get("context", {})

    style = context.get("tone", "professional")
    signature = context.get("signature", "")

    prompt = (
        f"You are ReplyMint, an assistant that drafts concise, helpful email replies in a {style} tone.\n"
        f"Original email from {sender}:\nSubject: {subject}\n\n{body}\n\n"
        f"Write a reply that is polite, clear, and actionable."
    )
    if signature:
        prompt += f"\n\nEnd the reply with this signature, if appropriate:\n{signature}"
    return prompt


def generate_reply(email: Dict[str, Any], max_tokens: int = 400) -> str:
    """Generate an email reply using GPT-4o Mini."""
    client = _client()
    prompt = build_prompt(email)

    logger.info("Generating AI reply", extra={"max_tokens": max_tokens})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write email replies."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content if response.choices else ""
    return content.strip()


