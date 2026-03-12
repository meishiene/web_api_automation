param(
    [ValidateSet("local", "test")]
    [string]$TargetEnv = "local",
    [switch]$SkipCompose,
    [int]$TimeoutSeconds = 90
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$alembicPath = Join-Path $repoRoot ".venv\Scripts\alembic.exe"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$composeFile = Join-Path $repoRoot "docker-compose.postgres.yml"
$healthScript = Join-Path $repoRoot "scripts\db_connectivity_check.py"

function Assert-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing required command: $Name"
    }
}

function Wait-PostgresHealthy([int]$Timeout) {
    $containerName = "web_api_automation_postgres"
    $deadline = (Get-Date).AddSeconds($Timeout)

    while ((Get-Date) -lt $deadline) {
        $status = docker inspect --format "{{.State.Health.Status}}" $containerName 2>$null
        if ($LASTEXITCODE -eq 0 -and $status -eq "healthy") {
            return
        }
        Start-Sleep -Seconds 2
    }

    throw "PostgreSQL container did not become healthy within ${Timeout}s."
}

Assert-Command "docker"

if (-not (Test-Path $alembicPath)) {
    throw "Alembic executable not found at $alembicPath"
}
if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found at $pythonPath"
}

if (-not $SkipCompose) {
    docker compose -f $composeFile up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start docker compose services."
    }
}

Wait-PostgresHealthy -Timeout $TimeoutSeconds

$env:APP_ENV = $TargetEnv
$env:USE_POSTGRES = "true"

Push-Location $repoRoot
try {
    $env:PYTHONPATH = $repoRoot

    & $alembicPath upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "alembic upgrade head failed."
    }

    & $pythonPath $healthScript
    if ($LASTEXITCODE -ne 0) {
        throw "Database connectivity check failed."
    }

    Write-Host "PostgreSQL is ready for '$TargetEnv' environment."
}
finally {
    Pop-Location
}
