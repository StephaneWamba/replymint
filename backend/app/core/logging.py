"""Logging configuration for ReplyMint Backend"""
import os
import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime


class CloudWatchFormatter(logging.Formatter):
    """Custom formatter for CloudWatch structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON for CloudWatch"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging() -> None:
    """Setup application logging configuration"""
    settings = None

    try:
        from .config import get_settings
        settings = get_settings()
    except ImportError:
        # Fallback if config not available
        pass

    # Determine log level
    log_level = getattr(settings, 'log_level', 'INFO') if settings else 'INFO'
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler for local development
    if not is_aws_lambda():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        # Use simple format for local development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Set specific logger levels
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Create logger for this application
    app_logger = logging.getLogger('replymint')
    app_logger.setLevel(numeric_level)

    # Add CloudWatch formatter if in AWS
    if is_aws_lambda():
        # In AWS Lambda, logs go to CloudWatch automatically
        # We just need to ensure proper formatting
        pass


def is_aws_lambda() -> bool:
    """Check if running in AWS Lambda environment"""
    return bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME'))


def log_with_context(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    """Log message with additional context fields"""
    extra_fields = {k: v for k, v in kwargs.items() if v is not None}

    if extra_fields:
        # Create a new record with extra fields
        record = logger.makeRecord(
            logger.name, logging.INFO, "", 0, message, (), None
        )
        record.extra_fields = extra_fields
        logger.handle(record)
    else:
        logger.info(message)


# Import os at module level for is_aws_lambda function
