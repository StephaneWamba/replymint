# Update a single SSM Parameter for ReplyMint (Example)
# Copy this file to update-ssm.ps1 for local use.

param(
    [Parameter(Mandatory = $true)]
    [string]$Environment,

    [Parameter(Mandatory = $true)]
    [string]$ParameterName,

    [Parameter(Mandatory = $true)]
    [string]$Value,

    [string]$Type = "SecureString",
    [string]$Region = "eu-central-1"
)

Write-Host "Updating SSM parameter for ReplyMint $Environment"

try { aws sts get-caller-identity | Out-Null }
catch { Write-Host "AWS not configured. Run 'aws configure' first."; exit 1 }

$FullParameterName = "/replymint/$Environment/$ParameterName"

aws ssm put-parameter `
  --name $FullParameterName `
  --value $Value `
  --type $Type `
  --overwrite | Out-Null

Write-Host "Updated: $FullParameterName"
aws ssm get-parameter --name $FullParameterName --with-decryption
