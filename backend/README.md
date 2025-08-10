# ReplyMint Backend

AI-powered email auto-reply service backend built with FastAPI on AWS Lambda.

## Architecture

- **Runtime**: Python 3.11 on AWS Lambda
- **Framework**: FastAPI with Mangum adapter
- **Infrastructure**: AWS SAM (Serverless Application Model)
- **Database**: DynamoDB (on-demand billing)
- **Region**: eu-central-1 (Frankfurt)

## Prerequisites

- Python 3.11 (required - do not use 3.12+)
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Docker (for SAM builds)

## Local Development

### Setup

1. Create virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (create `.env` file):

```env
ENVIRONMENT=staging
AWS_REGION=eu-central-1
LOG_LEVEL=DEBUG
```

### Running Locally

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using SAM local
sam local start-api --env-vars env.json
```

## Deployment

### Staging (Default)

```bash
# Using PowerShell script
.\deploy.ps1 staging

# Or manually
sam build --use-container
sam deploy --stack-name replymint-staging --parameter-overrides "Environment=staging LogRetentionDays=14" --capabilities CAPABILITY_IAM
```

### Production

```bash
# Using PowerShell script
.\deploy.ps1 prod

# Or manually
sam build --use-container
sam deploy --stack-name replymint-prod --parameter-overrides "Environment=prod LogRetentionDays=30" --capabilities CAPABILITY_IAM
```

## Infrastructure

### DynamoDB Tables

- `replymint-{env}-users` - User accounts and plans
- `replymint-{env}-usage-counters` - Monthly usage tracking
- `replymint-{env}-email-logs` - Email processing logs (30-day TTL)
- `replymint-{env}-settings` - User preferences and configuration

### SSM Parameters

All secrets and configuration are stored in AWS Systems Manager Parameter Store:

```
/replymint/{env}/
├── MAILGUN_API_KEY (SecureString)
├── MAILGUN_DOMAIN_OUTBOUND
├── MAILGUN_DOMAIN_INBOUND
├── STRIPE_SECRET_KEY (SecureString)
├── OPENAI_API_KEY (SecureString)
├── JWT_SECRET (SecureString)
└── ALLOWED_ORIGINS
```

#### Setting Up SSM Parameters

Since you don't have access to the AWS GUI, use the provided PowerShell scripts:

**Quick Setup (Recommended):**

```powershell
# Set up staging environment with all parameters
.\setup-aws.ps1 -Environment staging

# Set up production environment
.\setup-aws.ps1 -Environment prod
```

**Update Individual Parameters:**

```powershell
# Update with real credentials
.\update-ssm.ps1 -Environment staging -ParameterName MAILGUN_API_KEY -Value "your_actual_key"
.\update-ssm.ps1 -Environment staging -ParameterName OPENAI_API_KEY -Value "your_openai_key"
```

**View Parameters:**

```powershell
# List all parameters for staging
aws ssm get-parameters-by-path --path "/replymint/staging/" --recursive --with-decryption
```

See `SSM_SETUP.md` for detailed instructions and `SSM_QUICK_REFERENCE.md` for common commands.

### IAM Roles

- **Lambda Execution Role**: DynamoDB access, SSM parameter read, CloudWatch metrics
- **Least Privilege**: Only necessary permissions for the specific resources

## API Endpoints

### Health & Status

- `GET /health` - Basic health check
- `GET /ready` - Readiness check with dependency verification
- `GET /info` - Service information

### Webhooks

- `POST /webhooks/mailgun/inbound` - Mailgun inbound email processing
- `POST /webhooks/mailgun/events` - Mailgun delivery events
- `POST /webhooks/stripe` - Stripe subscription events

### API (v1)

- `GET /api/v1/dashboard/overview` - Dashboard summary
- `GET /api/v1/logs` - Email logs with pagination
- `GET /api/v1/settings` - User settings
- `PUT /api/v1/settings` - Update user settings
- `POST /api/v1/api-key/generate` - Generate new API key
- `DELETE /api/v1/api-key/{key_id}` - Revoke API key

## Environment Variables

| Variable               | Description                     | Default      |
| ---------------------- | ------------------------------- | ------------ |
| `ENVIRONMENT`          | Environment name (staging/prod) | staging      |
| `AWS_REGION`           | AWS region                      | eu-central-1 |
| `LOG_LEVEL`            | Logging level                   | INFO         |
| `USERS_TABLE`          | DynamoDB users table name       | Auto-set     |
| `USAGE_COUNTERS_TABLE` | DynamoDB usage table name       | Auto-set     |
| `EMAIL_LOGS_TABLE`     | DynamoDB logs table name        | Auto-set     |
| `SETTINGS_TABLE`       | DynamoDB settings table name    | Auto-set     |

## Monitoring & Observability

### CloudWatch

- **Logs**: Structured JSON logging with environment-specific retention
- **Metrics**: Lambda invocations, errors, duration
- **Alarms**: Error rate, latency thresholds

### Health Checks

- **Health**: Basic service availability
- **Ready**: Dependency connectivity verification
- **Info**: Configuration and table information

## Security

- **CORS**: Environment-specific allowed origins
- **Trusted Hosts**: Production host validation
- **SSM**: Secure parameter storage with encryption
- **IAM**: Least privilege access policies
- **Webhooks**: Signature verification (implemented in Epic 2-3)

## Development Workflow

1. **Local Development**: Use uvicorn for fast iteration
2. **Testing**: SAM local for Lambda environment testing
3. **Staging**: Deploy to staging environment for integration testing
4. **Production**: Tagged releases with manual approval

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure Python 3.11 is used
2. **Dependencies**: Check `requirements.txt` and virtual environment
3. **AWS Credentials**: Verify AWS CLI configuration
4. **SSM Parameters**: Ensure parameters exist in Parameter Store

### Logs

- **Local**: Console output with configured formatter
- **AWS**: CloudWatch Logs with structured JSON format

## Next Steps

This Epic 1 implementation provides the foundation. Future epics will add:

- **Epic 2**: Email pipeline implementation
- **Epic 3**: Stripe billing integration
- **Epic 4**: Authentication and dashboard
- **Epic 5**: AI generation and compression
- **Epic 6**: Usage tracking and quotas
- **Epic 7**: Security hardening and monitoring
- **Epic 8**: Admin tooling and documentation

## Support

For issues and questions:

1. Check CloudWatch logs for errors
2. Verify SSM parameters are set correctly
3. Test health endpoints for dependency issues
4. Review IAM permissions if access denied
