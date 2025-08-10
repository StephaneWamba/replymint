"""Configuration management for ReplyMint Backend"""
import os
from typing import List, Optional
from functools import lru_cache
import boto3
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment and SSM"""

    # Environment
    environment: str = Field(default="staging", env="ENVIRONMENT")

    # AWS
    aws_region: str = Field(default="eu-central-1", env="AWS_REGION")

    # DynamoDB Tables
    users_table: str = Field(env="USERS_TABLE")
    usage_counters_table: str = Field(env="USAGE_COUNTERS_TABLE")
    email_logs_table: str = Field(env="EMAIL_LOGS_TABLE")
    settings_table: str = Field(env="SETTINGS_TABLE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # CORS
    allowed_origins: List[str] = Field(default_factory=list)
    allowed_origin_regex: Optional[str] = None

    # Mailgun (loaded from SSM)
    mailgun_api_key: Optional[str] = None
    mailgun_domain_outbound: Optional[str] = None
    mailgun_domain_inbound: Optional[str] = None

    # Stripe (loaded from SSM)
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # OpenAI (loaded from SSM)
    openai_api_key: Optional[str] = None

    # JWT (loaded from SSM)
    jwt_secret: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    settings = Settings()

    # Load SSM parameters if in AWS environment
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        load_ssm_parameters(settings)

    # Set default allowed origins based on environment
    if not settings.allowed_origins and not settings.allowed_origin_regex:
        if settings.environment == "prod":
            settings.allowed_origins = ["https://replymint.vercel.app"]
            settings.allowed_origin_regex = None
        else:
            # Allow the primary staging domain and all preview deployments
            settings.allowed_origins = ["https://replymint-staging.vercel.app"]
            settings.allowed_origin_regex = r"^https://replymint-staging.*\.vercel\.app$"

    return settings


def load_ssm_parameters(settings: Settings) -> None:
    """Load configuration from AWS SSM Parameter Store"""
    try:
        ssm = boto3.client('ssm', region_name=settings.aws_region)

        # Load all parameters for this environment
        response = ssm.get_parameters_by_path(
            Path=f"/replymint/{settings.environment}/",
            Recursive=True,
            WithDecryption=True
        )

        for param in response['Parameters']:
            param_name = param['Name'].split('/')[-1].lower()
            param_value = param['Value']

            # Map SSM parameter names to settings attributes
            if param_name == "mailgun_api_key":
                settings.mailgun_api_key = param_value
            elif param_name == "mailgun_domain_outbound":
                settings.mailgun_domain_outbound = param_value
            elif param_name == "mailgun_domain_inbound":
                settings.mailgun_domain_inbound = param_value
            elif param_name == "stripe_secret_key":
                settings.stripe_secret_key = param_value
            elif param_name == "stripe_webhook_secret":
                settings.stripe_webhook_secret = param_value
            elif param_name == "openai_api_key":
                settings.openai_api_key = param_value
            elif param_name == "jwt_secret":
                settings.jwt_secret = param_value
            elif param_name == "allowed_origins":
                settings.allowed_origins = [param_value]

    except Exception as e:
        # Log error but don't fail - use defaults
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load SSM parameters: {e}")
        logger.info("Using environment variable defaults")
