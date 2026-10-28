@echo off
cd /d "%~dp0"

set "SCRIPT=C:\Users\YourName\Projects\backup\ESD_backup.py"
set "LOG_DIR=C:\Backups\Logs"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install Python or add it to PATH.
    pause
    exit /b 1
)

python "%SCRIPT%"
set "CODE=%errorlevel%"

echo.
if %CODE% neq 0 (
    echo BACKUP FAILED - exit code %CODE%. See the logs in %LOG_DIR%
) else (
    echo Backup finished successfully.
)

pause
exit /b %CODE%