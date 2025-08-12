# Security Hardening Guide

## Overview

This document outlines the security measures implemented in the ReplyMint backend and provides recommendations for additional hardening.

## Implemented Security Measures

### 1. CORS Configuration

- **Restricted Origins**: Only allows requests from verified domains
  - Staging: `https://replymint-staging.vercel.app`
  - Production: `https://replymint.vercel.app`
- **Methods**: Limited to necessary HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
- **Headers**: Restricted to essential headers only
- **Credentials**: Disabled for security
- **Max Age**: 300 seconds for preflight caching

### 2. Security Headers

All responses include these security headers:

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block` - XSS protection for older browsers
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information
- **Permissions-Policy**: Restricts browser features (geolocation, microphone, camera)

### 3. Trusted Host Middleware

- **Production Only**: Restricts allowed hosts to verified domains
- **Local Development**: Allows localhost and 127.0.0.1 for development

### 4. API Gateway Security

- **CORS**: Configured at API Gateway level
- **Rate Limiting**: Implemented through API Gateway (configurable)
- **HTTPS Only**: All endpoints require HTTPS

### 5. Lambda Security

- **IAM Least Privilege**: Minimal permissions for Lambda execution
- **Environment Variables**: No secrets in code
- **VPC Isolation**: Can be enabled if needed

### 6. DynamoDB Security

- **Server-Side Encryption**: Enabled by default
- **IAM Policies**: Least privilege access
- **VPC Endpoints**: Can be configured for additional isolation

## Security Recommendations

### 1. Authentication & Authorization

- **API Keys**: Implement API key authentication for external clients
- **JWT Tokens**: Use short-lived JWT tokens for user sessions
- **Rate Limiting**: Implement per-user rate limiting

### 2. Input Validation

- **Request Validation**: Validate all incoming requests
- **SQL Injection**: Use parameterized queries (already implemented with Pydantic)
- **XSS Prevention**: Sanitize user inputs

### 3. Monitoring & Alerting

- **CloudWatch Alarms**: Configured for error rates and latency
- **Log Analysis**: Monitor logs for suspicious activity
- **Metrics**: Track API usage patterns

### 4. Network Security

- **VPC**: Consider placing Lambda in VPC for additional isolation
- **Security Groups**: Restrict network access if using VPC
- **WAF**: Consider AWS WAF for additional protection

### 5. Secrets Management

- **AWS SSM**: Store secrets in Parameter Store
- **Rotation**: Implement automatic secret rotation
- **Access Control**: Limit access to secrets

## Security Checklist

### Before Production

- [ ] Enable VPC for Lambda functions
- [ ] Configure WAF rules
- [ ] Set up CloudTrail logging
- [ ] Implement API key authentication
- [ ] Add request validation middleware
- [ ] Configure log retention policies
- [ ] Set up security monitoring alerts

### Ongoing Security

- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Access key rotation
- [ ] Security patch updates
- [ ] Penetration testing

## Incident Response

### Security Breach Response

1. **Immediate Actions**

   - Isolate affected resources
   - Revoke compromised credentials
   - Enable enhanced logging

2. **Investigation**

   - Review CloudWatch logs
   - Check CloudTrail for unauthorized access
   - Analyze API Gateway access logs

3. **Recovery**
   - Restore from backups if needed
   - Implement additional security measures
   - Update incident response procedures

## Compliance

### GDPR Considerations

- **Data Minimization**: Only collect necessary data
- **Right to Erasure**: Implement user data deletion
- **Data Portability**: Allow data export
- **Consent Management**: Track user consent

### SOC 2 Preparation

- **Access Control**: Document access management
- **Change Management**: Track infrastructure changes
- **Incident Response**: Document procedures
- **Monitoring**: Implement comprehensive logging

## Resources

- [AWS Security Best Practices](https://aws.amazon.com/security/security-learning/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [AWS Lambda Security](https://docs.aws.amazon.com/lambda/latest/dg/security.html)
