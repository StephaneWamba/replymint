# SSM Quick Reference Card

## 🚀 Quick Start

```powershell
# 1. Set up staging environment (creates all parameters with placeholders)
.\setup-aws.ps1 -Environment staging

# 2. Update with real credentials
.\update-ssm.ps1 -Environment staging -ParameterName MAILGUN_API_KEY -Value "key-1234567890abcdef"
.\update-ssm.ps1 -Environment staging -ParameterName OPENAI_API_KEY -Value "sk-your-openai-key"
.\update-ssm.ps1 -Environment staging -ParameterName STRIPE_SECRET_KEY -Value "sk_test_your_stripe_key"

# 3. Deploy
.\deploy.ps1
```

## 📋 Common Commands

### View Parameters

```powershell
# List all parameters for an environment
aws ssm get-parameters-by-path --path "/replymint/staging/" --recursive --with-decryption

# Get specific parameter
aws ssm get-parameter --name "/replymint/staging/MAILGUN_API_KEY" --with-decryption
```

### Update Parameters

```powershell
# Using the update script (recommended)
.\update-ssm.ps1 -Environment staging -ParameterName MAILGUN_API_KEY -Value "new_value"

# Direct AWS CLI
aws ssm put-parameter --name "/replymint/staging/MAILGUN_API_KEY" --value "new_value" --type "SecureString" --overwrite
```

### Delete Parameters

```powershell
# Delete specific parameter
aws ssm delete-parameter --name "/replymint/staging/MAILGUN_API_KEY"

# Delete all parameters for an environment (be careful!)
aws ssm get-parameters-by-path --path "/replymint/staging/" --recursive --query "Parameters[].Name" --output text | ForEach-Object { aws ssm delete-parameter --name $_ }
```

## 🔐 Required Parameters

| Parameter                 | Type         | Description                    |
| ------------------------- | ------------ | ------------------------------ |
| `MAILGUN_API_KEY`         | SecureString | Your Mailgun API key           |
| `MAILGUN_DOMAIN_OUTBOUND` | String       | Domain for sending emails      |
| `MAILGUN_DOMAIN_INBOUND`  | String       | Domain for receiving emails    |
| `STRIPE_SECRET_KEY`       | SecureString | Stripe secret key (test/live)  |
| `OPENAI_API_KEY`          | SecureString | OpenAI API key                 |
| `JWT_SECRET`              | SecureString | Random 32+ character string    |
| `ALLOWED_ORIGINS`         | String       | CORS origins (comma-separated) |

## 🌍 Environment Setup

### Staging

```powershell
.\setup-aws.ps1 -Environment staging
# Then update with test credentials
```

### Production

```powershell
.\setup-aws.ps1 -Environment prod
# Then update with live credentials
```

## 🧪 Testing

```powershell
# Test AWS connection
aws sts get-caller-identity

# Test parameter access
aws ssm describe-parameters --max-items 1

# Test parameter creation
aws ssm put-parameter --name "/replymint/test/test" --value "test" --type "String"
aws ssm delete-parameter --name "/replymint/test/test"
```

## 🚨 Troubleshooting

### Permission Denied

- Check if your AWS credentials have `ssm:*` permissions
- Verify you're using the correct region (`eu-central-1`)

### Parameter Not Found

- Check exact parameter path: `/replymint/{environment}/{name}`
- Parameter names are case-sensitive

### Invalid Type

- Use `SecureString` for secrets (API keys, passwords)
- Use `String` for non-sensitive data (URLs, domains)

## 📱 Mobile-Friendly Commands

For quick mobile reference, here are the essential commands:

```bash
# View all staging parameters
aws ssm get-parameters-by-path --path "/replymint/staging/" --recursive

# Update a parameter
aws ssm put-parameter --name "/replymint/staging/MAILGUN_API_KEY" --value "new_key" --type "SecureString" --overwrite

# Test connection
aws sts get-caller-identity
```

## 🔄 Workflow

1. **Initial Setup**: Run `setup-aws.ps1` for each environment
2. **Update Credentials**: Use `update-ssm.ps1` to replace placeholders
3. **Verify**: Check parameters with `get-parameters-by-path`
4. **Deploy**: Run `deploy.ps1` to deploy the SAM application
5. **Test**: Verify health endpoints are working

## 💡 Pro Tips

- **Always use SecureString** for API keys and secrets
- **Test in staging first** before updating production
- **Keep a backup** of your parameter values somewhere secure
- **Use the update script** instead of direct AWS CLI for consistency
- **Check permissions** if you get access denied errors
