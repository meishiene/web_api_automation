param(
    [int]$Port = 8000,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Stop-ProcessSafe([int]$ProcessId, [switch]$ForceKill) {
    try {
        Stop-Process -Id $ProcessId -Force:$ForceKill -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Get-UvicornProcessIds([int]$TargetPort) {
    $patternPort = "--port\s+$TargetPort(\s|$)"
    try {
        $candidates = Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match "uvicorn" -and
            $_.CommandLine -match "app\.main:app" -and
            $_.CommandLine -match $patternPort
        }
        return @($candidates.ProcessId)
    }
    catch {
        return @()
    }
}

function Get-ListeningProcessIds([int]$TargetPort) {
    $connections = $null
    try {
        $connections = Get-NetTCPConnection -LocalPort $TargetPort -State Listen -ErrorAction Stop
    }
    catch {
        $connections = $null
    }

    if ($connections) {
        return @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
    }

    # Fallback for restricted environments where Get-NetTCPConnection is unavailable.
    $output = netstat -ano -p tcp
    $pids = @()
    foreach ($line in $output) {
        if ($line -match "^\s*TCP\s+\S+:$TargetPort\s+\S+\s+LISTENING\s+(\d+)\s*$") {
            $pids += [int]$Matches[1]
        }
    }
    return @($pids | Select-Object -Unique)
}

$stopped = [System.Collections.Generic.List[int]]::new()

$listenerPids = Get-ListeningProcessIds -TargetPort $Port
foreach ($procId in $listenerPids) {
    if (Stop-ProcessSafe -ProcessId $procId -ForceKill:$Force) {
        $stopped.Add($procId) | Out-Null
    }
}

# Fallback for cases where process isn't listening yet but command line exists.
if ($stopped.Count -eq 0) {
    $uvicornPids = Get-UvicornProcessIds -TargetPort $Port
    foreach ($procId in $uvicornPids) {
        if (Stop-ProcessSafe -ProcessId $procId -ForceKill:$Force) {
            $stopped.Add($procId) | Out-Null
        }
    }
}

# Handle leftover listener process (e.g. spawned reload worker).
Start-Sleep -Milliseconds 500
$listenerPids = Get-ListeningProcessIds -TargetPort $Port
foreach ($procId in $listenerPids) {
    if ($stopped.Contains($procId)) {
        continue
    }
    if (Stop-ProcessSafe -ProcessId $procId -ForceKill:$Force) {
        $stopped.Add($procId) | Out-Null
    }
}

if ($stopped.Count -eq 0) {
    Write-Host "No API process found on port $Port."
    exit 0
}

$stoppedList = ($stopped | Sort-Object -Unique) -join ", "
Write-Host "Stopped API process IDs: $stoppedList"
