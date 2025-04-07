@echo off
echo ===================================================
echo Creating Cisco Meraki CLU Distribution Package
echo ===================================================
echo.

set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%
set PACKAGE_NAME=CiscoMerakiCLU_%TIMESTAMP%.zip

echo Creating distribution package: %PACKAGE_NAME%
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell is available'" > nul 2>&1
if %errorlevel% neq 0 (
    echo PowerShell is not available. Cannot create zip file.
    pause
    exit /b 1
)

REM Create a temporary directory for the distribution
set TEMP_DIR=dist_temp
if exist %TEMP_DIR% rmdir /s /q %TEMP_DIR%
mkdir %TEMP_DIR%

REM Copy necessary files to the temp directory
echo Copying files to temporary directory...
xcopy /E /I /Y *.py %TEMP_DIR%\
xcopy /E /I /Y *.md %TEMP_DIR%\
xcopy /E /I /Y *.txt %TEMP_DIR%\
xcopy /E /I /Y *.bat %TEMP_DIR%\
xcopy /E /I /Y /EXCLUDE:%TEMP_DIR% modules %TEMP_DIR%\modules\
xcopy /E /I /Y /EXCLUDE:%TEMP_DIR% utilities %TEMP_DIR%\utilities\
xcopy /E /I /Y /EXCLUDE:%TEMP_DIR% static %TEMP_DIR%\static\

REM Remove files we don't want to include
if exist "%TEMP_DIR%\create_distribution_package.bat" del "%TEMP_DIR%\create_distribution_package.bat"

REM Create the zip file using PowerShell
echo Creating zip file...
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%PACKAGE_NAME%' -Force"

REM Clean up
echo Cleaning up temporary files...
rmdir /s /q %TEMP_DIR%

echo.
if exist "%PACKAGE_NAME%" (
    echo Distribution package created successfully: %PACKAGE_NAME%
    echo.
    echo Package location: %~dp0%PACKAGE_NAME%
    echo.
    echo This package contains:
    echo  - The complete Cisco Meraki CLU application
    echo  - Setup script (setup.bat)
    echo  - Comprehensive setup guide (SETUP_GUIDE.md)
    echo  - Distribution README (DISTRIBUTION_README.md)
    echo  - Requirements file (requirements.txt)
    echo.
    echo Share this package with your coworkers. They only need to:
    echo  1. Extract the zip file
    echo  2. Run setup.bat
    echo  3. Launch the application using the created shortcut
    echo.
) else (
    echo Failed to create distribution package.
)

pause
