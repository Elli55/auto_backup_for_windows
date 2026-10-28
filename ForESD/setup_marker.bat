@echo off
cd /d "%~dp0"

echo This will create the marker file in: %CD%\Backups
set /p ANSWER=Continue? (y/n): 
if /i not "%ANSWER%"=="y" goto :end

if not exist "Backups" mkdir "Backups"
type nul > "Backups\marker_backup.txt"
echo Marker created.

:end
pause