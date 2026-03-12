param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$TaskName = "web-api-automation-audit-governance",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_DELETES_SCHEDULED_TASK"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}

$schtasksArgs = @(
    "/Delete",
    "/F",
    "/TN", $TaskName
)

if ($DryRun) {
    Write-Host "[DRY RUN] schtasks command:"
    Write-Host "schtasks $($schtasksArgs -join ' ')"
    exit 0
}

& schtasks @schtasksArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to delete scheduled task: $TaskName"
}

Write-Host "Scheduled task deleted: $TaskName"
