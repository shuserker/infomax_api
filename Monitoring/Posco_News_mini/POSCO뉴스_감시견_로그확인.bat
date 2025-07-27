@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo POSCO News Monitor - Watchdog Log
echo ========================================

if exist watchdog.log (
    echo Watchdog Log (Last 30 lines):
    echo ----------------------------------------
    powershell "Get-Content watchdog.log -Tail 30"
    echo ----------------------------------------
) else (
    echo No watchdog log file found.
)

echo.
if exist watchdog_status.json (
    echo Current Status:
    echo ----------------------------------------
    type watchdog_status.json
    echo ----------------------------------------
) else (
    echo No status file found.
)

echo.
echo Available Commands:
echo - POSCO News Complete Automation Start.bat : Start automation
echo - POSCO News Complete Automation Stop.bat  : Stop automation
echo - POSCO News Watchdog Log Check.bat : Check logs
echo.
pause