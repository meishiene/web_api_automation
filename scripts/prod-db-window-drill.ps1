param(
    [Parameter(Mandatory = $true)]
    [string]$ConfirmText,
    [string]$DatabaseUrl = "",
    [string]$TargetRevision = "head",
    [string]$BootstrapRevision = "fcf57b5ad65c",
    [string]$ReportDir = ".\artifacts\prod-db-window-drill",
    [switch]$SkipConnectivityCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$requiredConfirmText = "I_UNDERSTAND_THIS_IS_DB_WINDOW_DRILL"
if ($ConfirmText -ne $requiredConfirmText) {
    throw "Invalid ConfirmText. Re-run with -ConfirmText '$requiredConfirmText'."
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$migrateScript = Join-Path $repoRoot "scripts\prod-db-migrate.ps1"
$rollbackScript = Join-Path $repoRoot "scripts\prod-db-rollback.ps1"

if (-not (Test-Path $migrateScript)) {
    throw "Missing script: $migrateScript"
}
if (-not (Test-Path $rollbackScript)) {
    throw "Missing script: $rollbackScript"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$startedAt = (Get-Date).ToString("o")
$resolvedReportDir = $ReportDir
if (-not [System.IO.Path]::IsPathRooted($resolvedReportDir)) {
    $resolvedReportDir = Join-Path $repoRoot $ReportDir
}
New-Item -ItemType Directory -Path $resolvedReportDir -Force | Out-Null
$manifestDir = Join-Path $resolvedReportDir "manifests"
New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null
$generatedDrillDatabase = $false

if (-not $DatabaseUrl) {
    $drillDbFile = Join-Path $repoRoot "tmp\prod_window_drill_${timestamp}.db"
    $drillDbDir = Split-Path -Parent $drillDbFile
    New-Item -ItemType Directory -Path $drillDbDir -Force | Out-Null
    $DatabaseUrl = "sqlite:///./tmp/prod_window_drill_${timestamp}.db"
    $generatedDrillDatabase = $true
}

$reportJsonPath = Join-Path $resolvedReportDir "window_drill_${timestamp}.json"
$reportMarkdownPath = Join-Path $resolvedReportDir "window_drill_${timestamp}.md"

$steps = @()
$overallStatus = "completed"
$errorMessage = $null
$migrationManifestPath = $null
$rollbackTargetRevision = $null

function Add-StepResult {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Note = ""
    )
    $script:steps += [ordered]@{
        name = $Name
        status = $Status
        note = $Note
        at = (Get-Date).ToString("o")
    }
}

Push-Location $repoRoot
try {
    if ($generatedDrillDatabase) {
        $alembicPath = Join-Path $repoRoot ".venv\Scripts\alembic.exe"
        if (-not (Test-Path $alembicPath)) {
            $alembicCommand = Get-Command alembic -ErrorAction SilentlyContinue
            if ($alembicCommand) {
                $alembicPath = $alembicCommand.Source
            }
        }
        if (-not (Test-Path $alembicPath)) {
            throw "Alembic executable not found. Expected .venv\\Scripts\\alembic.exe or alembic in PATH."
        }

        $env:DATABASE_URL = $DatabaseUrl
        $env:APP_ENV = "prod"
        $env:USE_POSTGRES = "true"
        $env:PYTHONPATH = $repoRoot

        try {
            & $alembicPath upgrade $BootstrapRevision
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to bootstrap drill database to revision $BootstrapRevision."
            }
            Add-StepResult -Name "bootstrap_drill_database" -Status "completed" -Note "revision=$BootstrapRevision"
        }
        catch {
            Add-StepResult -Name "bootstrap_drill_database" -Status "failed" -Note $_.Exception.Message
            throw
        }
    }

    try {
        & $migrateScript `
            -ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION `
            -DatabaseUrl $DatabaseUrl `
            -TargetRevision $TargetRevision `
            -ManifestDir $manifestDir `
            -SkipBackup `
            -SkipConnectivityCheck:$SkipConnectivityCheck
        Add-StepResult -Name "migrate_to_target" -Status "completed"
    }
    catch {
        Add-StepResult -Name "migrate_to_target" -Status "failed" -Note $_.Exception.Message
        throw
    }

    $latestManifest = Get-ChildItem -Path $manifestDir -Filter "prod_migration_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latestManifest) {
        throw "No migration manifest found in $manifestDir"
    }
    $migrationManifestPath = $latestManifest.FullName
    $manifestPayload = Get-Content -LiteralPath $migrationManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $rollbackTargetRevision = [string]$manifestPayload.pre_revision

    try {
        & $rollbackScript `
            -ConfirmText I_UNDERSTAND_THIS_WILL_ROLLBACK_PRODUCTION `
            -ManifestPath $migrationManifestPath `
            -DatabaseUrl $DatabaseUrl `
            -SkipConnectivityCheck:$SkipConnectivityCheck
        Add-StepResult -Name "rollback_to_pre_revision" -Status "completed" -Note "target=$rollbackTargetRevision"
    }
    catch {
        Add-StepResult -Name "rollback_to_pre_revision" -Status "failed" -Note $_.Exception.Message
        throw
    }

    try {
        & $migrateScript `
            -ConfirmText I_UNDERSTAND_THIS_IS_PRODUCTION `
            -DatabaseUrl $DatabaseUrl `
            -TargetRevision $TargetRevision `
            -ManifestDir $manifestDir `
            -SkipBackup `
            -SkipConnectivityCheck:$SkipConnectivityCheck
        Add-StepResult -Name "migrate_back_to_target" -Status "completed"
    }
    catch {
        Add-StepResult -Name "migrate_back_to_target" -Status "failed" -Note $_.Exception.Message
        throw
    }
}
catch {
    $overallStatus = "failed"
    $errorMessage = $_.Exception.Message
}
finally {
    Pop-Location
}

$report = [ordered]@{
    status = $overallStatus
    started_at = $startedAt
    database_url = $DatabaseUrl
    target_revision = $TargetRevision
    rollback_target_revision = $rollbackTargetRevision
    migration_manifest_path = $migrationManifestPath
    report_json_path = $reportJsonPath
    report_markdown_path = $reportMarkdownPath
    steps = $steps
    error_message = $errorMessage
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportJsonPath -Encoding UTF8

$lines = @()
$lines += "# Production DB Window Drill Report"
$lines += ""
$lines += "- Status: $overallStatus"
$lines += "- Started At: $($report.started_at)"
$lines += "- Database URL: $DatabaseUrl"
$lines += "- Target Revision: $TargetRevision"
$lines += "- Rollback Target Revision: $rollbackTargetRevision"
$lines += "- Migration Manifest: $migrationManifestPath"
$lines += ""
$lines += "## Steps"
foreach ($step in $steps) {
    $noteSuffix = if ($step.note) { " ($($step.note))" } else { "" }
    $lines += "- $($step.name): $($step.status)$noteSuffix"
}
if ($errorMessage) {
    $lines += ""
    $lines += "## Error"
    $lines += "- $errorMessage"
}
$lines | Set-Content -LiteralPath $reportMarkdownPath -Encoding UTF8

Write-Host "Window drill report JSON: $reportJsonPath"
Write-Host "Window drill report Markdown: $reportMarkdownPath"

if ($overallStatus -ne "completed") {
    exit 1
}
