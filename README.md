# ReplyMint

AI-powered email auto-reply SaaS built with Next.js frontend and FastAPI backend.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (required - do not use 3.12+)
- Node.js 18+ and npm/yarn
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Docker (for SAM builds)

### Environment Setup

1. Clone the repository

```bash
git clone https://github.com/StephaneWamba/replymint.git
cd replymint
```

2. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

3. Frontend Setup

```bash
cd frontend
npm install
```

## 🏗️ Architecture

### Backend (FastAPI + AWS Lambda)

- Runtime: Python 3.11 on AWS Lambda
- Framework: FastAPI with Mangum adapter
- Infrastructure: AWS SAM (Serverless Application Model)
- Database: DynamoDB (on-demand billing)
- Region: eu-central-1 (Frankfurt)

### Frontend (Next.js + Vercel)

- Framework: Next.js 14 with App Router
- Deployment: Vercel
- Authentication: NextAuth.js with magic links
- Styling: Tailwind CSS

## 🚀 Deployment

### Backend Deployment

Staging (Default):

```bash
# From repo root
./scripts/deploy-backend.ps1 staging
```

Production:

```bash
# From repo root
./scripts/deploy-backend.ps1 prod
```

### Frontend Deployment

The frontend automatically deploys to Vercel:

- Staging: `replymint-staging.vercel.app`
- Production: `replymint.vercel.app`

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
ENVIRONMENT=staging
AWS_REGION=eu-central-1
LOG_LEVEL=DEBUG
```

### Frontend Environment Variables

Set these in your Vercel project:

```env
NEXTAUTH_URL=https://your-domain.vercel.app
NEXTAUTH_SECRET=your-secret-key
STRIPE_SECRET_KEY=your-stripe-secret
STRIPE_WEBHOOK_SECRET=your-webhook-secret
NEXT_PUBLIC_STRIPE_PRICE_ID=your-price-id
NEXT_PUBLIC_BACKEND_API_URL=your-backend-api-url
```

### AWS SSM Parameters

Use the consolidated script to initialize/update/list parameters:

```powershell
# Initialize placeholders for staging
./scripts/aws-ssm.ps1 -Action init -Environment staging

# Update specific parameters
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName STRIPE_SECRET_KEY -Value sk_test_xxx
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName STRIPE_WEBHOOK_SECRET -Value whsec_xxx

# List parameters
./scripts/aws-ssm.ps1 -Action list -Environment staging
```

Backend expects these parameters in AWS Systems Manager:

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

## 🧪 Testing

Backend Tests:

```bash
cd backend
pytest
```

Frontend Tests:

```bash
cd frontend
npm test
```

## 📊 Monitoring

Health Checks:
- Backend: `/health`, `/ready`, `/info`
- Frontend: Built-in Vercel health monitoring

CloudWatch:
- Logs: Structured JSON logging
- Metrics: Lambda invocations, errors, duration
- Alarms: Error rate, latency thresholds

## 🔒 Security

- CORS: Environment-specific allowed origins
- Trusted Hosts: Production host validation
- SSM: Secure parameter storage with encryption
- IAM: Least privilege access policies
- Webhooks: Signature verification (Epics 2-3)

## 📁 Project Structure

```
replymint/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Test files
│   ├── template.yaml       # SAM template
│   ├── samconfig.toml      # SAM configuration
│   └── requirements.txt    # Python dependencies
├── frontend/                # Next.js frontend
│   ├── src/app/            # App Router pages
│   ├── src/components/     # React components
│   └── package.json        # Node.js dependencies
├── scripts/                 # Project scripts
│   ├── aws-ssm.ps1         # SSM management
│   └── deploy-backend.ps1  # SAM deploy wrapper
├── docs/                    # Developer guides
│   ├── mailgun.md
│   └── stripe.md
└── .github/                 # GitHub Actions workflows
```

## 🚀 CI/CD Pipeline

GitHub Actions:
- Push to main: Auto-deploy to staging
- Tagged releases: Deploy to production (manual approval)
- Path-based triggers: Only deploy changed components

Environments:
- Staging: `replymint-staging.vercel.app` + AWS staging stack
- Production: `replymint.vercel.app` + AWS production stack

## 📚 Documentation

- Mailgun: docs/mailgun.md
- Stripe: docs/stripe.md

## 🆘 Troubleshooting

Common Issues:
1. Python version must be 3.11
2. AWS CLI credentials configured (`aws configure`)
3. SSM parameters exist in Parameter Store
4. Dependencies installed (requirements.txt, package.json)
