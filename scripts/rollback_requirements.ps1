param(
    [string]$BackupFile = "requirements.lock",
    [string]$TargetFile = "requirements.txt",
    [string]$VenvPath = ".venv"
)

Write-Host "=== Restoring last known-good requirements ==="

if (!(Test-Path $BackupFile)) {
    Write-Host "No backup lock file found. Cannot roll back."
    exit 1
}

Copy-Item $BackupFile $TargetFile -Force
Write-Host "Restored $TargetFile from $BackupFile"

$Pip = Join-Path $VenvPath "Scripts\pip.exe"

Write-Host "Rebuilding environment"
& $Pip install -r $TargetFile

Write-Host "=== Rollback complete ==="
