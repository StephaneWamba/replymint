# Stripe Setup (Test/Staging and Production)

This guide configures Stripe products/prices and webhooks for ReplyMint.

Prerequisites:
- Stripe account
- Backend deployed (API Gateway URL)
- AWS SSM access

## 1) Products & Prices (Test mode first)
Create 3 products with monthly prices:
- Starter: 200 replies
- Growth: 1000 replies
- Scale: 3000 replies

Record price IDs in Vercel env vars (frontend):
- `NEXT_PUBLIC_STRIPE_PRICE_ID_STARTER`
- `NEXT_PUBLIC_STRIPE_PRICE_ID_GROWTH`
- `NEXT_PUBLIC_STRIPE_PRICE_ID_SCALE`

## 2) Webhook Endpoint
Use your API Gateway base URL per environment:
- Staging: https://<staging-id>.execute-api.eu-central-1.amazonaws.com/staging
- Production: https://<prod-id>.execute-api.eu-central-1.amazonaws.com/prod

Endpoint:
- `<BASE_URL>/webhooks/stripe`

Example (staging):
```
https://XXXX.execute-api.eu-central-1.amazonaws.com/staging/webhooks/stripe
```

## 3) Payload Styles (v1 thin vs v2 snapshot)
Stripe may create separate destinations for different payload styles.
- Snapshot (v2): larger, includes embedded object data
- Thin (v1): minimal payload; fetch details via API if needed

Our current backend handler accepts both at the same endpoint and logs the event. Full processing is planned for later epics.

## 4) Webhook Signing Secret
After creating the webhook endpoint, Stripe provides a signing secret (e.g., `whsec_...`). Store it in SSM:
```
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName STRIPE_WEBHOOK_SECRET -Value whsec_xxx
```
Also store the API key in SSM:
```
./scripts/aws-ssm.ps1 -Action update -Environment staging -ParameterName STRIPE_SECRET_KEY -Value sk_test_xxx
```

## 5) Testing
- Stripe Dashboard > Developers > Webhooks > Send Test Event to the endpoint
- Confirm 2xx response
- Check CloudWatch logs for the event type/payload size

Common events to enable:
- `customer.created`, `customer.subscription.*`
- `checkout.session.completed`
- `invoice.*`, `payment_intent.*`

## 6) Frontend Env Vars (Vercel)
Set in Vercel (staging):
- `NEXT_PUBLIC_BACKEND_API_URL`
- `NEXT_PUBLIC_STRIPE_PRICE_ID_*`

## 7) Troubleshooting
- 401 Invalid signature: ensure the correct `STRIPE_WEBHOOK_SECRET` is in SSM
- 500 Internal error: check Lambda logs for import/async issues
- No events received: verify the URL has no whitespace and is publicly reachable
