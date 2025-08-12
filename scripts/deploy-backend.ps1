# ReplyMint Backend Deployment Script
# Usage: .\deploy-backend.ps1 [staging|prod] [-Force]

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("staging", "prod")]
    [string]$Environment = "staging",
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

Write-Host "Deploying ReplyMint Backend to $Environment environment..." -ForegroundColor Green

# Resolve important paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..')).Path
$BackendDir = Join-Path $RepoRoot 'backend'

# Set environment-specific parameters
if ($Environment -eq "prod") {
    $StackName = "replymint-prod"
    $LogRetention = 30
    Write-Host "PRODUCTION DEPLOYMENT - Manual approval required" -ForegroundColor Yellow
}
else {
    $StackName = "replymint-staging"
    $LogRetention = 14
}

Write-Host "Log retention: $LogRetention days" -ForegroundColor Yellow

# Generate unique S3 bucket name for deployment artifacts
$Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$RandomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$S3BucketName = "replymint-$Environment-$Timestamp-$RandomSuffix"

Write-Host "Creating S3 bucket: $S3BucketName" -ForegroundColor Blue

# Create S3 bucket for deployment artifacts
try {
    aws s3 mb s3://$S3BucketName --region eu-central-1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "S3 bucket created successfully: $S3BucketName" -ForegroundColor Green
    }
    else {
        Write-Host "Failed to create S3 bucket" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error creating S3 bucket: $_" -ForegroundColor Red
    exit 1
}

# Build the SAM application from backend directory
Write-Host "Building SAM application..." -ForegroundColor Blue
Push-Location $BackendDir
sam build --use-container --cached

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Prepare deployment parameters
$DeployParams = @(
    "--stack-name", $StackName,
    "--s3-bucket", $S3BucketName,
    "--capabilities", "CAPABILITY_IAM",
    "--parameter-overrides",
    "Environment=$Environment",
    "LogRetentionDays=$LogRetention",
    "--region", "eu-central-1"
)

if ($Force) {
    $DeployParams += "--no-confirm-changeset"
}

# Deploy to the specified environment
Write-Host "Deploying to $StackName using S3 bucket: $S3BucketName" -ForegroundColor Blue
sam deploy @DeployParams

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Pop-Location

Write-Host "Deployment completed successfully!" -ForegroundColor Green

# Get the API URL
Write-Host "Getting API URL..." -ForegroundColor Blue
$ApiUrl = aws cloudformation describe-stacks --stack-name $StackName --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text --region eu-central-1

if ($ApiUrl) {
    Write-Host "API URL: $ApiUrl" -ForegroundColor Green
    Write-Host "Health check: $ApiUrl/health" -ForegroundColor Cyan
    Write-Host "Readiness check: $ApiUrl/ready" -ForegroundColor Cyan
    
    # Test health endpoint
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10  # Wait for deployment to stabilize
    
    try {
        $Response = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get -TimeoutSec 30
        Write-Host "Health check passed: $($Response.status)" -ForegroundColor Green
    }
    catch {
        Write-Warning "Health check failed: $($_.Exception.Message)"
    }
}
else {
    Write-Host "Could not retrieve API URL" -ForegroundColor Yellow
}

# Display CloudWatch dashboard info
Write-Host "CloudWatch Dashboard:" -ForegroundColor Yellow
Write-Host "   - Import from: docs/cloudwatch-dashboard.json" -ForegroundColor White
Write-Host "   - Update ACCOUNT_ID in the dashboard file" -ForegroundColor White

# Display security info
Write-Host "Security Features Enabled:" -ForegroundColor Yellow
Write-Host "   - CORS restricted to verified domains" -ForegroundColor White
Write-Host "   - Security headers on all responses" -ForegroundColor White
Write-Host "   - CloudWatch alarms for errors and latency" -ForegroundColor White
Write-Host "   - Log retention: $LogRetention days" -ForegroundColor White

# Display notification system info
Write-Host "Notification System:" -ForegroundColor Yellow
Write-Host "   - Direct CloudWatch → Lambda → Slack notifications" -ForegroundColor White
Write-Host "   - No SNS dependency - more reliable architecture" -ForegroundColor White
Write-Host "   - Slack webhook configured via SSM parameters" -ForegroundColor White

Write-Host "Deployment script completed!" -ForegroundColor Green
Write-Host "S3 bucket used: $S3BucketName" -ForegroundColor Cyan
Write-Host "Check CloudWatch for metrics and alarms." -ForegroundColor Green
