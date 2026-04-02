$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$nodeCommand = "node"
$runnerPath = Join-Path $repoRoot "scripts\dev-runner.mjs"

if (-not (Test-Path $runnerPath)) {
  throw "Missing dev runner: $runnerPath"
}

$dryRun = $false
if ($args -contains "-DryRun" -or $args -contains "--dry-run") {
  $dryRun = $true
}

Push-Location -LiteralPath $repoRoot
try {
  if ($dryRun) {
    & $nodeCommand $runnerPath --dry-run
  } else {
    & $nodeCommand $runnerPath
  }
} finally {
  Pop-Location
}
