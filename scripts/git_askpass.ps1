param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $PromptParts
)

$prompt = ($PromptParts -join " ").Trim()

if (-not $env:GITHUB_USERNAME) {
  Write-Error "GITHUB_USERNAME is not set"
  exit 1
}
if (-not $env:GITHUB_TOKEN) {
  Write-Error "GITHUB_TOKEN is not set"
  exit 1
}

# Git will call this helper twice: once for username and once for password/token.
if ($prompt -match "(?i)username") {
  Write-Output $env:GITHUB_USERNAME
  exit 0
}

# GitHub requires a Personal Access Token (PAT) for HTTPS Git operations.
Write-Output $env:GITHUB_TOKEN
exit 0

