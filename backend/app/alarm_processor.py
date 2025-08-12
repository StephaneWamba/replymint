"""CloudWatch Alarm Processor for ReplyMint Backend"""
import json
import logging
import os
from typing import Dict, Any
import asyncio

from .slack_notifications import process_cloudwatch_alarm

logger = logging.getLogger(__name__)


async def _async_handle(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Async implementation that processes CloudWatch alarms directly"""
    try:
        logger.info("Processing CloudWatch alarm notification directly")

        environment = os.environ.get('ENVIRONMENT', 'staging')
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

        if not webhook_url:
            logger.warning(
                "SLACK_WEBHOOK_URL not configured, skipping Slack notification")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Slack webhook not configured',
                    'alarms_processed': 0
                })
            }

        # Process CloudWatch alarm event directly
        alarms_processed = 0
        alarms_failed = 0

        try:
            # CloudWatch sends alarm data directly in the event
            # Extract alarm information from the CloudWatch event
            alarm_data = {
                'AlarmName': event.get('detail', {}).get('alarmName', 'Unknown Alarm'),
                'AlarmDescription': event.get('detail', {}).get('alarmDescription', 'No description'),
                'NewStateValue': event.get('detail', {}).get('state', {}).get('value', 'Unknown'),
                'OldStateValue': event.get('detail', {}).get('previousState', {}).get('value', 'Unknown'),
                'NewStateReason': event.get('detail', {}).get('state', {}).get('reason', 'No reason provided'),
                'StateChangeTime': event.get('time', 'Unknown')
            }

            logger.info(
                f"Processing CloudWatch alarm: {alarm_data['AlarmName']}")

            # Process the alarm and send to Slack
            success = await process_cloudwatch_alarm(
                alarm_data,
                webhook_url,
                environment
            )

            if success:
                alarms_processed += 1
                logger.info(
                    f"Successfully processed alarm: {alarm_data['AlarmName']}")
            else:
                alarms_failed += 1
                logger.error(
                    f"Failed to process alarm: {alarm_data['AlarmName']}")

        except Exception as e:
            alarms_failed += 1
            logger.error(f"Error processing CloudWatch alarm event: {e}")
            logger.error(f"Event structure: {json.dumps(event, default=str)}")

        logger.info(
            f"Alarm processing complete. Processed: {alarms_processed}, Failed: {alarms_failed}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alarm processing complete',
                'alarms_processed': alarms_processed,
                'alarms_failed': alarms_failed
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error in alarm processor: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Synchronous AWS Lambda handler that runs async logic safely."""
    return asyncio.run(_async_handle(event, context))


# For local testing
async def test_alarm_processor():
    """Test function for local development"""
    # Simulate CloudWatch alarm event structure
    test_event = {
        'version': '0',
        'id': 'test-alarm-id',
        'detail-type': 'CloudWatch Alarm State Change',
        'source': 'aws.cloudwatch',
        'account': '123456789012',
        'time': '2025-08-11T10:00:00.000Z',
        'region': 'eu-central-1',
        'detail': {
            'alarmName': 'test-replymint-error-rate',
            'alarmDescription': 'Test alarm for high error rate',
            'state': {
                'value': 'ALARM',
                'reason': 'Threshold Crossed: 1 out of the last 1 datapoints was greater than the threshold (5.0)'
            },
            'previousState': {
                'value': 'OK',
                'reason': 'Threshold Crossed: 1 out of the last 1 datapoints was greater than the threshold (5.0)'
            }
        }
    }

    result = await _async_handle(test_event, None)
    print(f"Test result: {result}")


if __name__ == "__main__":
    asyncio.run(test_alarm_processor())
