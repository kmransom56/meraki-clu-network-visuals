# Log monitoring script for Meraki CLI
# This script monitors both debug and error logs in real-time

$debugLog = "meraki_clu_debug.log"
$errorLog = "log\error.log"

Write-Host "Starting log monitoring..." -ForegroundColor Green
Write-Host "Monitoring: $debugLog and $errorLog" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

# Function to display log entries with colors
function Show-LogEntry {
    param($line, $logType)
    
    if ($logType -eq "ERROR") {
        Write-Host "[$logType] " -ForegroundColor Red -NoNewline
        Write-Host $line
    } elseif ($line -match "ERROR|Exception|Traceback|Failed") {
        Write-Host "[DEBUG] " -ForegroundColor Yellow -NoNewline
        Write-Host $line
    } else {
        Write-Host "[DEBUG] " -ForegroundColor Gray -NoNewline
        Write-Host $line
    }
}

# Monitor both log files
$watchers = @()

# Watch debug log
if (Test-Path $debugLog) {
    $watcher1 = Get-Content $debugLog -Wait -Tail 0
    Start-Job -ScriptBlock {
        param($file)
        Get-Content $file -Wait -Tail 0 | ForEach-Object {
            Show-LogEntry $_ "DEBUG"
        }
    } -ArgumentList (Resolve-Path $debugLog) | Out-Null
}

# Watch error log
if (Test-Path $errorLog) {
    $watcher2 = Get-Content $errorLog -Wait -Tail 0
    Start-Job -ScriptBlock {
        param($file)
        Get-Content $file -Wait -Tail 0 | ForEach-Object {
            Show-LogEntry $_ "ERROR"
        }
    } -ArgumentList (Resolve-Path $errorLog) | Out-Null
}

# Simple approach: Poll the files
Write-Host "Monitoring logs (polling every 1 second)..." -ForegroundColor Green
Write-Host ""

$debugLastSize = 0
$errorLastSize = 0

try {
    while ($true) {
        # Check debug log
        if (Test-Path $debugLog) {
            $currentSize = (Get-Item $debugLog).Length
            if ($currentSize -gt $debugLastSize) {
                $newContent = Get-Content $debugLog -Tail 10
                foreach ($line in $newContent) {
                    if ($line -and $line.Length -gt 0) {
                        Show-LogEntry $line "DEBUG"
                    }
                }
                $debugLastSize = $currentSize
            }
        }
        
        # Check error log
        if (Test-Path $errorLog) {
            $currentSize = (Get-Item $errorLog).Length
            if ($currentSize -gt $errorLastSize) {
                $newContent = Get-Content $errorLog -Tail 10
                foreach ($line in $newContent) {
                    if ($line -and $line.Length -gt 0) {
                        Show-LogEntry $line "ERROR"
                    }
                }
                $errorLastSize = $currentSize
            }
        }
        
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "Monitoring stopped." -ForegroundColor Yellow
}
