param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$TargetRevision = "",
    [string]$ManifestPath = "",
    [string]$DatabaseUrl = "",
    [switch]$SkipConnectivityCheck,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$alembicPath = Join-Path $repoRoot ".venv\Scripts\alembic.exe"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$healthScript = Join-Path $repoRoot "scripts\db_connectivity_check.py"

if ($ManifestPath) {
    if (-not (Test-Path $ManifestPath)) {
        throw "Manifest file not found: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $TargetRevision) {
        $TargetRevision = [string]$manifest.pre_revision
    }
}

if (-not $TargetRevision) {
    throw "Target revision is required. Pass -TargetRevision or provide -ManifestPath with pre_revision."
}

if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}

$env:APP_ENV = "prod"
$env:USE_POSTGRES = "true"
$env:PYTHONPATH = $repoRoot

if ($DryRun) {
    Write-Host "[DRY RUN] Production rollback plan:"
    Write-Host "  APP_ENV=prod"
    Write-Host "  USE_POSTGRES=true"
    Write-Host "  DATABASE_URL=***configured***"
    Write-Host "  Step 1: alembic downgrade $TargetRevision"
    if (-not $SkipConnectivityCheck) {
        Write-Host "  Step 2: run db_connectivity_check.py"
    }
    exit 0
}

if (-not (Test-Path $alembicPath)) {
    $alembicCommand = Get-Command alembic -ErrorAction SilentlyContinue
    if ($alembicCommand) {
        $alembicPath = $alembicCommand.Source
    }
}
if (-not (Test-Path $pythonPath)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $pythonPath = $pythonCommand.Source
    }
}
if (-not (Test-Path $alembicPath)) {
    throw "Alembic executable not found. Expected .venv\Scripts\alembic.exe or alembic in PATH."
}
if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found. Expected .venv\Scripts\python.exe or python in PATH."
}

if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required for production rollback. Set env DATABASE_URL or pass -DatabaseUrl; migration manifests do not store credentials."
}

Push-Location $repoRoot
try {
    & $alembicPath downgrade $TargetRevision
    if ($LASTEXITCODE -ne 0) {
        throw "alembic downgrade $TargetRevision failed."
    }
    Write-Host "Rollback applied: $TargetRevision"

    if (-not $SkipConnectivityCheck) {
        & $pythonPath $healthScript
        if ($LASTEXITCODE -ne 0) {
            throw "Connectivity/schema check failed after rollback."
        }
        Write-Host "Connectivity/schema check passed."
    }
}
finally {
    Pop-Location
}
