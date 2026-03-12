param(
    [ValidateSet("local", "test")]
    [string]$TargetEnv = "local",
    [switch]$SkipCompose,
    [int]$DbTimeoutSeconds = 90,
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoReload,
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$postgresUpScript = Join-Path $repoRoot "scripts\dev-postgres-up.ps1"
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $postgresUpScript)) {
    throw "Missing script: $postgresUpScript"
}
if (-not (Test-Path $pythonPath)) {
    throw "Python executable not found at $pythonPath"
}

Push-Location $repoRoot
try {
    & $postgresUpScript -TargetEnv $TargetEnv -SkipCompose:$SkipCompose -TimeoutSeconds $DbTimeoutSeconds
    if ($LASTEXITCODE -ne 0) {
        throw "Database preparation failed."
    }

    if ($PrepareOnly) {
        Write-Host "Database is ready. Skip starting API because -PrepareOnly was provided."
        return
    }

    $env:APP_ENV = $TargetEnv
    $env:USE_POSTGRES = "true"
    $env:PYTHONPATH = $repoRoot

    $uvicornArgs = @("-m", "uvicorn", "app.main:app", "--host", $BindHost, "--port", "$Port")
    if (-not $NoReload) {
        $uvicornArgs += "--reload"
    }

    & $pythonPath @uvicornArgs
}
finally {
    Pop-Location
}
