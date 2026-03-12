param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$TargetRevision = "head",
    [string]$DatabaseUrl = "",
    [switch]$SkipBackup,
    [switch]$SkipConnectivityCheck,
    [switch]$DryRun,
    [string]$BackupDir = ".\backups\prod-db"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_IS_PRODUCTION"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$alembicPath = Join-Path $repoRoot ".venv\Scripts\alembic.exe"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$healthScript = Join-Path $repoRoot "scripts\db_connectivity_check.py"

if (-not (Test-Path $alembicPath)) {
    throw "Alembic executable not found at $alembicPath"
}
if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found at $pythonPath"
}

if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
}

$env:APP_ENV = "prod"
$env:USE_POSTGRES = "true"
$env:PYTHONPATH = $repoRoot

if ($DryRun) {
    Write-Host "[DRY RUN] Production migration plan:"
    Write-Host "  APP_ENV=prod"
    Write-Host "  USE_POSTGRES=true"
    Write-Host "  DATABASE_URL=***configured***"
    if (-not $SkipBackup) {
        Write-Host "  Step 1: create backup by pg_dump"
    }
    Write-Host "  Step 2: alembic upgrade $TargetRevision"
    if (-not $SkipConnectivityCheck) {
        Write-Host "  Step 3: run db_connectivity_check.py"
    }
    exit 0
}

if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required for production migration. Set env DATABASE_URL or pass -DatabaseUrl."
}

Push-Location $repoRoot
try {
    if (-not $SkipBackup) {
        if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
            throw "pg_dump is required for backup. Install PostgreSQL client or use -SkipBackup."
        }

        $resolvedBackupDir = $BackupDir
        if (-not [System.IO.Path]::IsPathRooted($resolvedBackupDir)) {
            $resolvedBackupDir = Join-Path $repoRoot $BackupDir
        }
        New-Item -ItemType Directory -Path $resolvedBackupDir -Force | Out-Null

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = Join-Path $resolvedBackupDir "prod_backup_${timestamp}.dump"

        & pg_dump --format=custom --file $backupFile --dbname $env:DATABASE_URL --no-owner --no-privileges
        if ($LASTEXITCODE -ne 0) {
            throw "pg_dump backup failed."
        }
        Write-Host "Backup created: $backupFile"
    }

    & $alembicPath upgrade $TargetRevision
    if ($LASTEXITCODE -ne 0) {
        throw "alembic upgrade $TargetRevision failed."
    }
    Write-Host "Migration applied: $TargetRevision"

    if (-not $SkipConnectivityCheck) {
        & $pythonPath $healthScript
        if ($LASTEXITCODE -ne 0) {
            throw "Connectivity/schema check failed after migration."
        }
        Write-Host "Connectivity/schema check passed."
    }
}
finally {
    Pop-Location
}
