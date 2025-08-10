<#!
.SYNOPSIS
  Manage AWS SSM parameters for ReplyMint (initialize, update, list).

.DESCRIPTION
  Consolidated utility for working with SSM parameters per environment.
  Requires AWS CLI installed and configured (run: aws configure).

.PARAMETER Action
  One of: init, update, list

.PARAMETER Environment
  Target environment (default: staging). Examples: staging, prod

.PARAMETER Region
  AWS region (default: eu-central-1)

.PARAMETER ParameterName
  For update: name of the parameter (without the /replymint/<env>/ prefix)

.PARAMETER Value
  For update: value to set

.PARAMETER Type
  For update: SSM type, SecureString or String (default: SecureString)

.EXAMPLE
  # Initialize placeholders for staging
  ./aws-ssm.ps1 -Action init -Environment staging

.EXAMPLE
  # Update a specific parameter
  ./aws-ssm.ps1 -Action update -Environment staging -ParameterName STRIPE_SECRET_KEY -Value sk_test_xxx

.EXAMPLE
  # List all parameters for an environment
  ./aws-ssm.ps1 -Action list -Environment staging
#>

param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("init", "update", "list")]
  [string]$Action,

  [string]$Environment = "staging",
  [string]$Region = "eu-central-1",

  [string]$ParameterName,
  [string]$Value,
  [ValidateSet("SecureString","String")]
  [string]$Type = "SecureString"
)

$ErrorActionPreference = "Stop"

function Ensure-AwsReady {
  Write-Host "Verifying AWS CLI..."
  try { aws --version | Out-Null } catch { Write-Error "AWS CLI not found. Install: https://aws.amazon.com/cli/" }

  Write-Host "Verifying AWS credentials..."
  try { aws sts get-caller-identity | Out-Null } catch { Write-Error "AWS CLI is not configured. Run 'aws configure' first." }

  Write-Host "Setting region/output..."
  aws configure set region $Region | Out-Null
  aws configure set output json | Out-Null
}

function Get-BasePath {
  return "/replymint/$Environment"
}

function Put-Param {
  param(
    [string]$Name,
    [string]$Val,
    [string]$ParamType = "SecureString",
    [string]$Desc = ""
  )
  $full = "$(Get-BasePath)/$Name"
  aws ssm put-parameter `
    --name $full `
    --value $Val `
    --type $ParamType `
    --description $Desc `
    --overwrite | Out-Null
  Write-Host "Upserted: $full"
}

function Action-Init {
  Write-Host "Initializing placeholder parameters for '$Environment'..."
  Put-Param -Name "MAILGUN_API_KEY" -Val "replace_me" -Desc "Mailgun API key for $Environment"
  Put-Param -Name "MAILGUN_DOMAIN_OUTBOUND" -Val "replace_me" -ParamType "String" -Desc "Mailgun outbound domain"
  Put-Param -Name "MAILGUN_DOMAIN_INBOUND" -Val "replace_me" -ParamType "String" -Desc "Mailgun inbound domain"

  Put-Param -Name "STRIPE_SECRET_KEY" -Val "replace_me" -Desc "Stripe secret key for $Environment"

  Put-Param -Name "OPENAI_API_KEY" -Val "replace_me" -Desc "OpenAI API key for $Environment"

  Put-Param -Name "JWT_SECRET" -Val "replace_me" -Desc "JWT secret for $Environment"
  Put-Param -Name "ALLOWED_ORIGINS" -Val "https://replymint.vercel.app,https://replymint-staging.vercel.app" -ParamType "String" -Desc "Allowed CORS origins"

  Put-Param -Name "SLACK_WEBHOOK_URL" -Val "replace_me" -Desc "Slack webhook URL (optional)"

  Write-Host "Listing created parameters..."
  aws ssm get-parameters-by-path --path (Get-BasePath) --recursive --with-decryption
}

function Action-Update {
  if (-not $ParameterName -or -not $Value) {
    Write-Error "For update: -ParameterName and -Value are required."
  }
  Write-Host "Updating parameter '$ParameterName' in '$Environment'..."
  Put-Param -Name $ParameterName -Val $Value -ParamType $Type
  Write-Host "Verifying update..."
  aws ssm get-parameter --name "$(Get-BasePath)/$ParameterName" --with-decryption
}

function Action-List {
  Write-Host "Listing parameters for '$Environment'..."
  aws ssm get-parameters-by-path --path (Get-BasePath) --recursive --with-decryption
}

Ensure-AwsReady
switch ($Action) {
  "init" { Action-Init }
  "update" { Action-Update }
  "list" { Action-List }
  default { Write-Error "Unknown action: $Action" }
}
