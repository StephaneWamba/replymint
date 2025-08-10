# Simple deployment script for ReplyMint backend
# This script creates the S3 bucket if it doesn't exist and deploys

param(
    [string]$Environment = "staging",
    [string]$Region = "eu-central-1"
)

Write-Host "Deploying ReplyMint backend to $Environment environment in $Region region..."

# Generate a unique S3 bucket name
$BucketName = "replymint-$Environment-$(Get-Date -Format 'yyyyMMdd')-$(Get-Random -Minimum 1000 -Maximum 9999)"

Write-Host "Creating S3 bucket: $BucketName"

# Create S3 bucket
try {
    aws s3 mb s3://$BucketName --region $Region
    Write-Host "S3 bucket created successfully: $BucketName"
} catch {
    Write-Host "Error creating S3 bucket: $_"
    exit 1
}

# Deploy using SAM
Write-Host "Deploying with SAM..."
sam deploy --stack-name "replymint-$Environment" --region $Region --capabilities CAPABILITY_IAM --parameter-overrides "Environment=$Environment" "LogRetentionDays=14" --s3-bucket $BucketName

Write-Host "Deployment completed!"
Write-Host "S3 bucket: $BucketName"
Write-Host "Stack name: replymint-$Environment"
