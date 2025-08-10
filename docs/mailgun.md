# Mailgun Setup (Staging and Production)

This guide configures Mailgun inbound and event webhooks for ReplyMint.

Prerequisites:
- Mailgun account and domain(s)
- Backend deployed to AWS API Gateway (staging and production)
- AWS SSM parameters created (see scripts/aws-ssm.ps1)

## 1) Domains
- Staging: use sandbox domain (or a verified subdomain)
- Production: verified domain (e.g., mail.yourdomain.com)

Record your domains in SSM:
```
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName MAILGUN_DOMAIN_OUTBOUND -Value your-staging-domain -Type String
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName MAILGUN_DOMAIN_INBOUND  -Value your-staging-domain -Type String
```

## 2) Webhook URLs
Get your API Gateway base URL per environment (from SAM deploy output):
- Staging: https://<staging-id>.execute-api.eu-central-1.amazonaws.com/staging
- Production: https://<prod-id>.execute-api.eu-central-1.amazonaws.com/prod

Endpoints:
- Inbound route target: `<BASE_URL>/webhooks/mailgun/inbound`
- Events webhook: `<BASE_URL>/webhooks/mailgun/events`

Example (staging):
```
Inbound: https://XXXX.execute-api.eu-central-1.amazonaws.com/staging/webhooks/mailgun/inbound
Events:  https://XXXX.execute-api.eu-central-1.amazonaws.com/staging/webhooks/mailgun/events
```

## 3) Configure Inbound Route
- Mailgun > Receiving > Routes > Create Route
- Pattern: Match recipient(s) you need, or "Catch All"
- Action: `forward("<BASE_URL>/webhooks/mailgun/inbound")`
- Optionally enable "Store and notify" for debugging

## 4) Configure Event Webhooks
- Mailgun > Sending > Webhooks
- Add webhook URL for events you care about (delivered, opened, clicked, bounced, complained, unsubscribed)
- Use: `<BASE_URL>/webhooks/mailgun/events`

## 5) Testing
- Send a test email to your inbound address (e.g., support@your-staging-domain)
- Check CloudWatch logs (Lambda) for inbound processing
- Use Mailgun webhook test to send sample events to the events endpoint

## 6) Security Notes
- Verify that your backend validates Mailgun webhooks (signature verification can be added in a later epic)
- Keep API keys in SSM:
```
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName MAILGUN_API_KEY -Value key-xxxxxxxx
```

## 7) Troubleshooting
- 502/500 on webhook: check Lambda logs for import/config errors
- No events: confirm Mailgun domain is verified and webhooks are active
- Inbound not firing: ensure route pattern matches the recipient address
