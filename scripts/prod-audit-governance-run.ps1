param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$DatabaseUrl = "",
    [int]$ActiveRetentionDays = 30,
    [int]$ArchiveRetentionDays = 180,
    [int]$BatchSize = 500,
    [string]$ManifestDir = ".\artifacts\audit-governance",
    [string]$LockFile = ".\artifacts\audit-governance\audit-governance.lock",
    [int]$MaxCandidateArchiveCount = -1,
    [int]$MaxCandidateDeleteArchiveCount = -1,
    [int]$MaxArchivedCount = -1,
    [int]$MaxDeletedArchiveCount = -1,
    [string]$AlertWebhookUrl = "",
    [string]$AlertTitle = "Audit Governance Alert",
    [string]$AlertOutput = ".\artifacts\audit-governance\last-alert.json",
    [switch]$FailOnAlert,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_IS_PRODUCTION"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$runnerScript = Join-Path $repoRoot "scripts\audit-governance-run.py"
$notifyScript = Join-Path $repoRoot "scripts\alert-webhook-notify.py"

if (-not (Test-Path $pythonPath)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $pythonPath = $pythonCommand.Source
    }
}
if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found. Expected .venv\Scripts\python.exe or python in PATH."
}
if (-not (Test-Path $runnerScript)) {
    throw "Runner script not found: $runnerScript"
}
if (-not (Test-Path $notifyScript)) {
    throw "Notify script not found: $notifyScript"
}

if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}
if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required for production audit governance. Set env DATABASE_URL or pass -DatabaseUrl."
}

$env:APP_ENV = "prod"
$env:USE_POSTGRES = "true"
$env:PYTHONPATH = $repoRoot

$args = @(
    $runnerScript,
    "--active-retention-days", "$ActiveRetentionDays",
    "--archive-retention-days", "$ArchiveRetentionDays",
    "--batch-size", "$BatchSize",
    "--manifest-dir", $ManifestDir,
    "--lock-file", $LockFile,
    "--alert-output", $AlertOutput
)

if ($MaxCandidateArchiveCount -ge 0) {
    $args += @("--max-candidate-archive-count", "$MaxCandidateArchiveCount")
}
if ($MaxCandidateDeleteArchiveCount -ge 0) {
    $args += @("--max-candidate-delete-archive-count", "$MaxCandidateDeleteArchiveCount")
}
if ($MaxArchivedCount -ge 0) {
    $args += @("--max-archived-count", "$MaxArchivedCount")
}
if ($MaxDeletedArchiveCount -ge 0) {
    $args += @("--max-deleted-archive-count", "$MaxDeletedArchiveCount")
}
if ($FailOnAlert) {
    $args += "--fail-on-alert"
}
if ($DryRun) {
    $args += "--dry-run"
}

Push-Location $repoRoot
try {
    $alertOutputPath = $AlertOutput
    if (-not [System.IO.Path]::IsPathRooted($alertOutputPath)) {
        $alertOutputPath = Join-Path $repoRoot $AlertOutput
    }
    if (Test-Path $alertOutputPath) {
        Remove-Item -LiteralPath $alertOutputPath -Force
    }

    & $pythonPath @args
    $runnerExitCode = $LASTEXITCODE
    $alertTriggered = Test-Path $alertOutputPath

    if ($AlertWebhookUrl -and ($runnerExitCode -ne 0 -or $alertTriggered)) {
        $notifySummary = if ($runnerExitCode -ne 0) {
            "Audit governance run failed (exit code $runnerExitCode)."
        }
        else {
            "Audit governance run exceeded alert threshold."
        }
        $notifyStatus = if ($runnerExitCode -ne 0) { "failed" } else { "alert" }
        $notifyArgs = @(
            $notifyScript,
            "--webhook-url", $AlertWebhookUrl,
            "--title", $AlertTitle,
            "--source", "prod-audit-governance-run.ps1",
            "--status", $notifyStatus,
            "--summary", $notifySummary
        )
        if ($alertTriggered) {
            $notifyArgs += @("--payload-file", $alertOutputPath)
        }
        & $pythonPath @notifyArgs
    }

    if ($runnerExitCode -ne 0) {
        throw "Audit governance run failed with exit code $runnerExitCode."
    }
}
finally {
    Pop-Location
}
