# ReplyMint Backend Deployment Script
# Usage: .\deploy-backend.ps1 [staging|prod]

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("staging", "prod")]
    [string]$Environment = "staging"
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
    } else {
        Write-Host "Failed to create S3 bucket" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error creating S3 bucket: $_" -ForegroundColor Red
    exit 1
}

# Build the SAM application from backend directory
Write-Host "Building SAM application..." -ForegroundColor Blue
Push-Location $BackendDir
sam build --use-container

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to the specified environment using the created S3 bucket
Write-Host "Deploying to $StackName using S3 bucket: $S3BucketName" -ForegroundColor Blue
sam deploy --stack-name $StackName --s3-bucket $S3BucketName --parameter-overrides "Environment=$Environment LogRetentionDays=$LogRetention" --capabilities CAPABILITY_IAM --region eu-central-1 --no-confirm-changeset

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
} else {
    Write-Host "Could not retrieve API URL" -ForegroundColor Yellow
}

Write-Host "Deployment script completed!" -ForegroundColor Green
Write-Host "S3 bucket used: $S3BucketName" -ForegroundColor Cyan
