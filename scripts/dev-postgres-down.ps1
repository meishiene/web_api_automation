param(
    [switch]$RemoveVolumes,
    [switch]$RemoveOrphans
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$composeFile = Join-Path $repoRoot "docker-compose.postgres.yml"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Missing required command: docker"
}

$args = @("compose", "-f", $composeFile, "down")
if ($RemoveVolumes) {
    $args += "-v"
}
if ($RemoveOrphans) {
    $args += "--remove-orphans"
}

Push-Location $repoRoot
try {
    docker @args
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to stop PostgreSQL docker compose service."
    }
}
finally {
    Pop-Location
}

Write-Host "PostgreSQL compose service has been stopped."
if ($RemoveVolumes) {
    Write-Host "Named volumes were removed."
}

