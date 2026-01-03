param(
    [string]$VenvPath = ".venv",
    [string]$Python = "python"
)

Write-Host "=== Environment Bootstrap Starting ==="

# 1. Create virtual environment
if (!(Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath"
    & $Python -m venv $VenvPath
} else {
    Write-Host "Virtual environment already exists"
}

$Pip = Join-Path $VenvPath "Scripts\pip.exe"

# 2. Upgrade pip
Write-Host "Upgrading pip"
& $Pip install --upgrade pip

# 3. Install dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt"
    & $Pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found — skipping install"
}

# 4. Validate environment
Write-Host "Validating environment"
& $Pip check

Write-Host "=== Bootstrap Complete ==="
