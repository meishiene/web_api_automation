param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [Parameter(Mandatory = $true)]
    [string]$DatabaseUrl,
    [string]$TaskName = "web-api-automation-audit-governance",
    [int]$IntervalMinutes = 60,
    [string]$AlertWebhookUrl = "",
    [switch]$FailOnAlert,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_CREATES_SCHEDULED_TASK"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}
if ($IntervalMinutes -lt 1) {
    throw "IntervalMinutes must be >= 1."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$prodScript = Join-Path $repoRoot "scripts\prod-audit-governance-run.ps1"
if (-not (Test-Path $prodScript)) {
    throw "Missing script: $prodScript"
}

$arguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$prodScript`"",
    "-ConfirmText", "I_UNDERSTAND_THIS_IS_PRODUCTION",
    "-DatabaseUrl", "`"$DatabaseUrl`""
)
if ($FailOnAlert) {
    $arguments += "-FailOnAlert"
}
if ($AlertWebhookUrl) {
    $arguments += @("-AlertWebhookUrl", "`"$AlertWebhookUrl`"")
}

$taskCommand = "powershell.exe " + ($arguments -join " ")
$schtasksArgs = @(
    "/Create",
    "/F",
    "/TN", $TaskName,
    "/TR", $taskCommand,
    "/SC", "MINUTE",
    "/MO", "$IntervalMinutes"
)

if ($DryRun) {
    Write-Host "[DRY RUN] schtasks command:"
    Write-Host "schtasks $($schtasksArgs -join ' ')"
    exit 0
}

& schtasks @schtasksArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create scheduled task."
}

Write-Host "Scheduled task created: $TaskName"
