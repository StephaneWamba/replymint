"""Health check endpoints for ReplyMint Backend"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
import boto3
from datetime import datetime

from ..core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "replymint-backend"
    }


@router.get("/ready")
async def readiness_check(settings=Depends(get_settings)) -> Dict[str, Any]:
    """Readiness check - verifies dependencies are available"""
    health_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "replymint-backend",
        "environment": settings.environment,
        "checks": {}
    }

    # Check DynamoDB connectivity
    try:
        dynamodb = boto3.client('dynamodb', region_name=settings.aws_region)
        dynamodb.describe_table(TableName=settings.users_table)
        health_status["checks"]["dynamodb"] = "healthy"
    except Exception as e:
        logger.warning(f"DynamoDB health check failed: {e}")
        health_status["checks"]["dynamodb"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check SSM parameter access
    try:
        ssm = boto3.client('ssm', region_name=settings.aws_region)
        ssm.get_parameters_by_path(
            Path=f"/replymint/{settings.environment}/",
            MaxResults=1
        )
        health_status["checks"]["ssm"] = "healthy"
    except Exception as e:
        logger.warning(f"SSM health check failed: {e}")
        health_status["checks"]["ssm"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status


@router.get("/info")
async def info(settings=Depends(get_settings)) -> Dict[str, Any]:
    """Service information endpoint"""
    return {
        "name": "ReplyMint Backend",
        "version": "0.1.0",
        "environment": settings.environment,
        "region": settings.aws_region,
        "tables": {
            "users": settings.users_table,
            "usage_counters": settings.usage_counters_table,
            "email_logs": settings.email_logs_table,
            "settings": settings.settings_table
        }
    }
