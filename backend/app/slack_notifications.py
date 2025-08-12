"""Slack notification handling for ReplyMint Backend"""
import json
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_slack_message(webhook_url: str, message: Dict[str, Any]) -> bool:
    """Send message to Slack webhook"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=message,
                timeout=10.0
            )
            response.raise_for_status()
            logger.info("Slack message sent successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return False


def format_alarm_message(alarm_data: Dict[str, Any], environment: str) -> Dict[str, Any]:
    """Format CloudWatch alarm data for Slack"""

    # Extract alarm information
    alarm_name = alarm_data.get('AlarmName', 'Unknown Alarm')
    alarm_description = alarm_data.get('AlarmDescription', 'No description')
    new_state = alarm_data.get('NewStateValue', 'Unknown')
    old_state = alarm_data.get('OldStateValue', 'Unknown')
    reason = alarm_data.get('NewStateReason', 'No reason provided')
    timestamp = alarm_data.get(
        'StateChangeTime', datetime.utcnow().isoformat())

    # Determine color based on alarm state
    if new_state == 'ALARM':
        color = '#ff0000'  # Red for alarm
        emoji = '🚨'
    elif new_state == 'OK':
        color = '#00ff00'  # Green for OK
        emoji = '✅'
    else:
        color = '#ffff00'  # Yellow for insufficient data
        emoji = '⚠️'

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        formatted_time = timestamp

    # Create Slack message
    message = {
        "attachments": [
            {
                "color": color,
                "title": f"{emoji} CloudWatch Alarm: {alarm_name}",
                "text": alarm_description,
                "fields": [
                    {
                        "title": "Environment",
                        "value": environment.upper(),
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": f"{old_state} → {new_state}",
                        "short": True
                    },
                    {
                        "title": "Reason",
                        "value": reason,
                        "short": False
                    },
                    {
                        "title": "Time",
                        "value": formatted_time,
                        "short": True
                    }
                ],
                "footer": "ReplyMint Backend Monitoring",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
    }

    return message


async def process_cloudwatch_alarm(alarm_data: Dict[str, Any], webhook_url: str, environment: str) -> bool:
    """Process CloudWatch alarm and send to Slack"""
    try:
        # Format the alarm message
        slack_message = format_alarm_message(alarm_data, environment)

        # Send to Slack
        success = await send_slack_message(webhook_url, slack_message)

        if success:
            logger.info(
                f"Alarm notification sent to Slack: {alarm_data.get('AlarmName', 'Unknown')}")
        else:
            logger.error(
                f"Failed to send alarm notification to Slack: {alarm_data.get('AlarmName', 'Unknown')}")

        return success

    except Exception as e:
        logger.error(f"Error processing CloudWatch alarm: {e}")
        return False
