# Import environment variables from a file with export KEY="VALUE" format
# into Windows environment variables.

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('User', 'System')]
    [string]$Scope = 'User',
    
    [switch]$DryRun
)

function Import-ExportEnvFile {
    param(
        [string]$FilePath,
        [string]$Scope = 'User',
        [bool]$DryRun = $false
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "Error: File not found: $FilePath" -ForegroundColor Red
        return @{Success = 0; Total = 0}
    }
    
    $envVars = @{}
    $lineNum = 0
    
    Get-Content $FilePath | ForEach-Object {
        $lineNum++
        $line = $_.Trim()
        
        # Skip empty lines and comments
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) {
            return
        }
        
        # Match both formats:
        # 1. export KEY="VALUE" or export KEY='VALUE' or export KEY=VALUE
        # 2. KEY="VALUE" or KEY='VALUE' or KEY=VALUE (INI format)
        if ($line -match '^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$') {
            $key = $matches[1]
            $value = $matches[2].Trim()
            
            # Remove surrounding quotes if present
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or 
                ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            
            # Handle escaped characters
            $value = $value -replace '\\"', '"' -replace "\\'", "'"
            
            $envVars[$key] = $value
        } else {
            Write-Host "Warning: Skipping line $lineNum (not in export KEY=`"VALUE`" format): $line" -ForegroundColor Yellow
        }
    }
    
    if ($envVars.Count -eq 0) {
        Write-Host "No environment variables found in file." -ForegroundColor Yellow
        return @{Success = 0; Total = 0}
    }
    
    Write-Host "`nFound $($envVars.Count) environment variable(s) to import:" -ForegroundColor Cyan
    foreach ($key in $envVars.Keys) {
        Write-Host "  - $key" -ForegroundColor Gray
    }
    
    if ($DryRun) {
        Write-Host "`n[DRY RUN MODE - No changes will be made]`n" -ForegroundColor Yellow
    }
    
    Write-Host "`nImporting to $Scope environment variables...`n" -ForegroundColor Cyan
    
    $successCount = 0
    $totalCount = $envVars.Count
    
    foreach ($key in $envVars.Keys) {
        $value = $envVars[$key]
        
        # Mask sensitive values in output
        if ($key -match 'key|password|secret|token' -and $value.Length -gt 0) {
            $displayValue = '*' * [Math]::Min($value.Length, 20)
            if ($value.Length -gt 20) { $displayValue += '...' }
        } else {
            $displayValue = if ($value.Length -gt 50) { $value.Substring(0, 50) + '...' } else { $value }
        }
        
        Write-Host "Setting $key=$displayValue" -ForegroundColor Gray
        
        if ($DryRun) {
            Write-Host "[DRY RUN] Would set $Scope environment variable: $key" -ForegroundColor Yellow
            $successCount++
        } else {
            try {
                if ($Scope -eq 'System') {
                    # System-wide requires admin
                    [System.Environment]::SetEnvironmentVariable($key, $value, 'Machine')
                } else {
                    # User scope
                    [System.Environment]::SetEnvironmentVariable($key, $value, 'User')
                }
                
                # Also set for current session
                [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
                
                Write-Host "✓ Set $Scope environment variable: $key" -ForegroundColor Green
                $successCount++
            } catch {
                Write-Host "✗ Failed to set $key : $_" -ForegroundColor Red
            }
        }
    }
    
    return @{Success = $successCount; Total = $totalCount}
}

# Check if running as admin for system scope
if ($Scope -eq 'System' -and -not $DryRun) {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "Warning: System-wide environment variables require Administrator privileges." -ForegroundColor Yellow
        Write-Host "Please run this script as Administrator or use -Scope User for user variables." -ForegroundColor Yellow
        $response = Read-Host "Continue anyway? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            exit 1
        }
    }
}

# Import the environment variables
$result = Import-ExportEnvFile -FilePath $FilePath -Scope $Scope -DryRun $DryRun

# Summary
Write-Host "`n$('='*60)" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "[DRY RUN] Would import $($result.Success)/$($result.Total) environment variables" -ForegroundColor Yellow
} else {
    Write-Host "Imported $($result.Success)/$($result.Total) environment variables" -ForegroundColor $(if ($result.Success -eq $result.Total) { 'Green' } else { 'Yellow' })
    if ($result.Success -eq $result.Total) {
        Write-Host "`n✓ All environment variables imported successfully!" -ForegroundColor Green
        Write-Host "`nNote: You may need to restart your terminal/application" -ForegroundColor Gray
        Write-Host "      for the changes to take effect in new processes." -ForegroundColor Gray
    } else {
        Write-Host "`n⚠ $($result.Total - $result.Success) environment variable(s) failed to import" -ForegroundColor Yellow
    }
}

exit $(if ($result.Success -eq $result.Total) { 0 } else { 1 })
