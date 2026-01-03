@echo off
echo ===================================================
echo Cisco Meraki CLU - Installation Script
echo ===================================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python is installed. Installing required packages...
echo.

REM Install required packages
uv pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

if %errorlevel% neq 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo Installation completed successfully!
echo.
echo To run the application:
echo   - Option 1: Run 'python main.py' from this directory
echo   - Option 2: Double-click on the 'start_meraki_clu.bat' file
echo.
echo For more information, please read the SETUP_GUIDE.md file.
echo ===================================================
echo.

REM Create a shortcut file for easy launching
echo @echo off > start_meraki_clu.bat
echo python "%~dp0main.py" >> start_meraki_clu.bat
echo.

echo Created start_meraki_clu.bat for easy launching.
echo.
pause
