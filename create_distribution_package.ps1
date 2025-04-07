# PowerShell script to create a distribution package for Cisco Meraki CLU
Write-Host "====================================================="
Write-Host "Creating Cisco Meraki CLU Distribution Package"
Write-Host "====================================================="
Write-Host ""

# Set timestamp and package name
$timestamp = Get-Date -Format "yyyyMMdd"
$packageName = "CiscoMerakiCLU_$timestamp.zip"

# Set the output directory
$outputDir = "C:\Users\keith.ransom\OneDrive - Inspire Brands\Documents - Retail Network\Inspire Brands\Retail Network\Above Brand\Tools and Contacts\Scripts\meraki\Meraki CLU Tool"

# Create the output directory if it doesn't exist
if (!(Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
    Write-Host "Created output directory: $outputDir"
}

Write-Host "Creating distribution package: $packageName"
Write-Host "Output location: $outputDir"
Write-Host ""

# Create a temporary directory
$tempDir = "dist_temp"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -Path $tempDir -ItemType Directory | Out-Null

# Define files and directories to include
$includeDirs = @(
    "modules",
    "utilities",
    "static",
    "api",
    "settings",
    "docs"
)

# Define files to include
$includeFiles = @(
    "main.py",
    "setup.py",
    "setup.bat",
    "requirements.txt",
    "README.md",
    "LICENSE",
    "SETUP_GUIDE.md",
    "DISTRIBUTION_README.md"
)

# Define patterns to exclude
$excludePatterns = @(
    "*.pyc",
    "*__pycache__*",
    "*.git*",
    "*.vscode*",
    "*.idea*",
    "*.log",
    "CiscoMerakiCLU_*.zip",
    "create_distribution_package.*"
)

# Copy directories
Write-Host "Copying directories..."
foreach ($dir in $includeDirs) {
    if (Test-Path $dir) {
        Write-Host "  - $dir"
        $destination = Join-Path $tempDir $dir
        New-Item -Path $destination -ItemType Directory -Force | Out-Null
        
        # Get all files in the directory, excluding patterns
        $files = Get-ChildItem -Path $dir -Recurse -File | 
                Where-Object { 
                    $file = $_.FullName
                    $exclude = $false
                    foreach ($pattern in $excludePatterns) {
                        if ($file -like $pattern) {
                            $exclude = $true
                            break
                        }
                    }
                    -not $exclude
                }
        
        # Copy each file
        foreach ($file in $files) {
            $relativePath = $file.FullName.Substring((Get-Location).Path.Length + 1)
            $destPath = Join-Path $tempDir $relativePath
            $destDir = Split-Path -Path $destPath -Parent
            
            if (-not (Test-Path $destDir)) {
                New-Item -Path $destDir -ItemType Directory -Force | Out-Null
            }
            
            Copy-Item -Path $file.FullName -Destination $destPath -Force
        }
    }
}

# Copy individual files
Write-Host "Copying files..."
foreach ($file in $includeFiles) {
    if (Test-Path $file) {
        Write-Host "  - $file"
        Copy-Item -Path $file -Destination $tempDir -Force
    }
}

# Create the zip file
$outputPath = Join-Path -Path $outputDir -ChildPath $packageName
Compress-Archive -Path "$tempDir\*" -DestinationPath $outputPath -Force

# Clean up
Write-Host "Cleaning up temporary files..."
Remove-Item -Path $tempDir -Recurse -Force

# Verify the package was created
if (Test-Path $outputPath) {
    Write-Host ""
    Write-Host "Distribution package created successfully: $packageName"
    Write-Host "Package location: $outputPath"
    Write-Host ""
    Write-Host "This package contains:"
    Write-Host "  - The complete Cisco Meraki CLU application"
    Write-Host "  - Setup script (setup.bat)"
    Write-Host "  - Comprehensive setup guide (SETUP_GUIDE.md)"
    Write-Host "  - Distribution README (DISTRIBUTION_README.md)"
    Write-Host "  - Requirements file (requirements.txt)"
    Write-Host ""
    Write-Host "Share this package with your coworkers. They only need to:"
    Write-Host "  1. Extract the zip file"
    Write-Host "  2. Run setup.bat"
    Write-Host "  3. Launch the application using the created shortcut"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Failed to create distribution package." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press any key to continue..."
