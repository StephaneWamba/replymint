# Setup AWS CLI and SSM Parameters for ReplyMint (Example)
# Copy this file to setup-aws.ps1 and fill in values as needed.
# Requires AWS CLI and configured credentials (run `aws configure`).

param(
    [string]$Environment = "staging",
    [string]$Region = "eu-central-1"
)

Write-Host "Setting up SSM Parameters for ReplyMint $Environment"

# Verify AWS CLI
try {
    aws --version | Out-Null
}
catch {
    Write-Host "AWS CLI not found. Install from https://aws.amazon.com/cli/"; exit 1
}

# Ensure caller identity
try {
    aws sts get-caller-identity | Out-Null
}
catch {
    Write-Host "AWS not configured. Run 'aws configure' first."; exit 1
}

$BasePath = "/replymint/$Environment"

function Create-SSMParameter {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Type = "SecureString",
        [string]$Description = ""
    )

    $FullName = "$BasePath/$Name"
    aws ssm put-parameter `
        --name $FullName `
        --value $Value `
        --type $Type `
        --description $Description `
        --overwrite | Out-Null
    Write-Host "Created: $FullName"
}

# Mailgun
Create-SSMParameter -Name "MAILGUN_API_KEY" -Value "replace_me" -Description "Mailgun API key for $Environment"
Create-SSMParameter -Name "MAILGUN_DOMAIN_OUTBOUND" -Value "replace_me" -Type "String" -Description "Mailgun outbound domain"
Create-SSMParameter -Name "MAILGUN_DOMAIN_INBOUND" -Value "replace_me" -Type "String" -Description "Mailgun inbound domain"

# Stripe
Create-SSMParameter -Name "STRIPE_SECRET_KEY" -Value "replace_me" -Description "Stripe secret key for $Environment"

# OpenAI
Create-SSMParameter -Name "OPENAI_API_KEY" -Value "replace_me" -Description "OpenAI API key for $Environment"

# Security
Create-SSMParameter -Name "JWT_SECRET" -Value "replace_me" -Description "JWT secret for $Environment"
Create-SSMParameter -Name "ALLOWED_ORIGINS" -Value "https://replymint.vercel.app,https://replymint-staging.vercel.app" -Type "String" -Description "Allowed CORS origins"

# Optional
Create-SSMParameter -Name "SLACK_WEBHOOK_URL" -Value "replace_me" -Description "Slack webhook URL (optional)"

Write-Host "Listing parameters:"
aws ssm get-parameters-by-path --path $BasePath --recursive --with-decryption
