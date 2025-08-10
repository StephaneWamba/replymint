# ReplyMint

AI-powered email auto-reply SaaS built with Next.js frontend and FastAPI backend.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (required - do not use 3.12+)
- **Node.js 18+** and npm/yarn
- **AWS CLI** configured with appropriate permissions
- **AWS SAM CLI** installed
- **Docker** (for SAM builds)

### Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/StephaneWamba/replymint.git
cd replymint
```

2. **Backend Setup**

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

## 🏗️ Architecture

### Backend (FastAPI + AWS Lambda)

- **Runtime**: Python 3.11 on AWS Lambda
- **Framework**: FastAPI with Mangum adapter
- **Infrastructure**: AWS SAM (Serverless Application Model)
- **Database**: DynamoDB (on-demand billing)
- **Region**: eu-central-1 (Frankfurt)

### Frontend (Next.js + Vercel)

- **Framework**: Next.js 14 with App Router
- **Deployment**: Vercel
- **Authentication**: NextAuth.js with magic links
- **Styling**: Tailwind CSS

## 🚀 Deployment

### Backend Deployment

#### Staging (Default)

```bash
cd backend
.\deploy.ps1 staging
```

#### Production

```bash
cd backend
.\deploy.ps1 prod
```

### Frontend Deployment

The frontend automatically deploys to Vercel:

- **Staging**: `replymint-staging.vercel.app`
- **Production**: `replymint.vercel.app`

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

The backend requires these parameters in AWS Systems Manager:

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

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 Monitoring

### Health Checks

- **Backend**: `/health`, `/ready`, `/info`
- **Frontend**: Built-in Vercel health monitoring

### CloudWatch

- **Logs**: Structured JSON logging
- **Metrics**: Lambda invocations, errors, duration
- **Alarms**: Error rate, latency thresholds

## 🔒 Security

- **CORS**: Environment-specific allowed origins
- **Trusted Hosts**: Production host validation
- **SSM**: Secure parameter storage with encryption
- **IAM**: Least privilege access policies
- **Webhooks**: Signature verification (Epic 2-3)

## 📁 Project Structure

```
replymint/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── core/          # Configuration, logging
│   │   ├── routers/       # API endpoints
│   │   ├── main.py        # FastAPI app
│   │   └── handler.py     # Lambda handler
│   ├── tests/             # Test files
│   ├── template.yaml      # SAM template
│   ├── samconfig.toml     # SAM configuration
│   ├── deploy.ps1         # Deployment script
│   └── requirements.txt   # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── lib/               # Utilities and config
│   └── package.json       # Node.js dependencies
├── .github/                # GitHub Actions workflows
└── internal/               # Project documentation
```

## 🚀 CI/CD Pipeline

### GitHub Actions

- **Push to main**: Auto-deploy to staging
- **Tagged releases**: Deploy to production (manual approval)
- **Path-based triggers**: Only deploy changed components

### Environments

- **Staging**: `replymint-staging.vercel.app` + AWS staging stack
- **Production**: `replymint.vercel.app` + AWS production stack

## 📋 Epic Progress

### ✅ Epic 1: Foundations (Current)

- [x] Backend scaffold with FastAPI
- [x] SAM template with DynamoDB tables
- [x] IAM roles and SSM parameter structure
- [x] Health endpoints and basic API structure
- [x] CI/CD pipeline setup
- [x] Environment-specific configurations

### 🔄 Upcoming Epics

- **Epic 2**: Email pipeline (Mailgun integration)
- **Epic 3**: Billing and provisioning (Stripe)
- **Epic 4**: Authentication and dashboard
- **Epic 5**: AI generation and compression
- **Epic 6**: Usage tracking and quotas
- **Epic 7**: Security hardening and monitoring
- **Epic 8**: Admin tooling and documentation

## 🛠️ Development Workflow

1. **Local Development**: Use uvicorn/fastapi for backend, Next.js dev server for frontend
2. **Testing**: Run tests locally before committing
3. **Staging**: Push to main triggers staging deployment
4. **Production**: Create tagged release for production deployment

## 🆘 Troubleshooting

### Common Issues

1. **Python Version**: Ensure Python 3.11 is used
2. **AWS Credentials**: Verify AWS CLI configuration
3. **SSM Parameters**: Ensure parameters exist in Parameter Store
4. **Dependencies**: Check requirements.txt and package.json

### Getting Help

1. Check CloudWatch logs for backend errors
2. Review Vercel deployment logs for frontend issues
3. Verify environment variables are set correctly
4. Test health endpoints for dependency issues

## 📚 Documentation

- [Backend README](backend/README.md) - Detailed backend setup and deployment
- [Frontend README](frontend/README.md) - Frontend development guide
- [Implementation Plan](internal/implementation_plan.md) - Overall project roadmap
- [Epic 1 Details](internal/epic1_foundations_todo.md) - Current epic specifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

---

**Status**: Epic 1 - Foundations ✅ Complete  
**Next**: Epic 2 - Email Pipeline Implementation
