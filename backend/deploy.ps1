# ReplyMint Backend Deployment Script
# Usage: .\deploy.ps1 [staging|prod]

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("staging", "prod")]
    [string]$Environment = "staging"
)

Write-Host "Deploying ReplyMint Backend to $Environment environment..." -ForegroundColor Green

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

# Build the SAM application
Write-Host "Building SAM application..." -ForegroundColor Blue
sam build --use-container

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to the specified environment
Write-Host "Deploying to $StackName..." -ForegroundColor Blue
sam deploy --stack-name $StackName --parameter-overrides "Environment=$Environment LogRetentionDays=$LogRetention" --capabilities CAPABILITY_IAM --no-confirm-changeset

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green

# Get the API URL
Write-Host "Getting API URL..." -ForegroundColor Blue
$ApiUrl = aws cloudformation describe-stacks --stack-name $StackName --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text --region eu-central-1

if ($ApiUrl) {
    Write-Host "API URL: $ApiUrl" -ForegroundColor Green
    Write-Host "Health check: $ApiUrl/health" -ForegroundColor Cyan
    Write-Host "Readiness check: $ApiUrl/ready" -ForegroundColor Cyan
}
else {
    Write-Host "Could not retrieve API URL" -ForegroundColor Yellow
}

Write-Host "Deployment script completed!" -ForegroundColor Green
