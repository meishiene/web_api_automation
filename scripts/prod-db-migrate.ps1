param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$TargetRevision = "head",
    [string]$DatabaseUrl = "",
    [switch]$SkipBackup,
    [switch]$SkipConnectivityCheck,
    [switch]$DryRun,
    [string]$BackupDir = ".\backups\prod-db",
    [string]$ManifestDir = ".\artifacts\prod-db-migrations"
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
$revisionScript = Join-Path $repoRoot "scripts\db_revision_check.py"

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
    Write-Host "  Step 0: capture current alembic revision and write manifest"
    if (-not $SkipBackup) {
        Write-Host "  Step 1: create backup by pg_dump"
    }
    Write-Host "  Step 2: alembic upgrade $TargetRevision"
    if (-not $SkipConnectivityCheck) {
        Write-Host "  Step 3: run db_connectivity_check.py"
    }
    Write-Host "  Step 4: record post-migration revision and finalize manifest"
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
if (-not (Test-Path $revisionScript)) {
    throw "Revision check script not found at $revisionScript"
}

if (-not $env:DATABASE_URL) {
    throw "DATABASE_URL is required for production migration. Set env DATABASE_URL or pass -DatabaseUrl."
}

Push-Location $repoRoot
try {
    $resolvedManifestDir = $ManifestDir
    if (-not [System.IO.Path]::IsPathRooted($resolvedManifestDir)) {
        $resolvedManifestDir = Join-Path $repoRoot $ManifestDir
    }
    New-Item -ItemType Directory -Path $resolvedManifestDir -Force | Out-Null

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $manifestPath = Join-Path $resolvedManifestDir "prod_migration_${timestamp}.json"
    $preRevisionPayload = & $pythonPath $revisionScript
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to query current alembic revision before migration."
    }
    $preRevisionData = $preRevisionPayload | ConvertFrom-Json

    $manifest = [ordered]@{
        started_at = (Get-Date).ToString("o")
        status = "started"
        target_revision = $TargetRevision
        pre_revision = $preRevisionData.current_revision
        post_revision = $null
        backup_file = $null
        rollback_command = $null
        connectivity_check_enabled = (-not $SkipConnectivityCheck)
        backup_enabled = (-not $SkipBackup)
    }

    $manifest.rollback_command = ('powershell -ExecutionPolicy Bypass -File .\scripts\prod-db-rollback.ps1 -ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION -ManifestPath "{0}" -DatabaseUrl "<required>"' -f $manifestPath)
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    if (-not $SkipBackup) {
        if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
            throw "pg_dump is required for backup. Install PostgreSQL client or use -SkipBackup."
        }

        $resolvedBackupDir = $BackupDir
        if (-not [System.IO.Path]::IsPathRooted($resolvedBackupDir)) {
            $resolvedBackupDir = Join-Path $repoRoot $BackupDir
        }
        New-Item -ItemType Directory -Path $resolvedBackupDir -Force | Out-Null

        $backupFile = Join-Path $resolvedBackupDir "prod_backup_${timestamp}.dump"

        & pg_dump --format=custom --file $backupFile --dbname $env:DATABASE_URL --no-owner --no-privileges
        if ($LASTEXITCODE -ne 0) {
            throw "pg_dump backup failed."
        }
        Write-Host "Backup created: $backupFile"
        $manifest.backup_file = $backupFile
        $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
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

    $postRevisionPayload = & $pythonPath $revisionScript
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to query current alembic revision after migration."
    }
    $postRevisionData = $postRevisionPayload | ConvertFrom-Json
    $manifest.post_revision = $postRevisionData.current_revision
    $manifest.status = "completed"
    $manifest.completed_at = (Get-Date).ToString("o")
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Write-Host "Migration manifest written: $manifestPath"
}
catch {
    if ($manifestPath) {
        $existingManifest = [ordered]@{}
        if (Test-Path $manifestPath) {
            $manifestObject = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($property in $manifestObject.PSObject.Properties) {
                $existingManifest[$property.Name] = $property.Value
            }
        }
        $existingManifest.status = "failed"
        $existingManifest.failed_at = (Get-Date).ToString("o")
        $existingManifest.error_message = $_.Exception.Message
        $existingManifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
        Write-Host "Migration manifest written: $manifestPath"
    }
    throw
}
finally {
    Pop-Location
}
