@echo off
chcp 65001 >nul
echo ========================================
echo POSCO News Monitor - Stop Automation
echo ========================================

echo Stopping watchdog process...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *watchdog*" 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_watchdog.py*" 2>nul

echo.
echo Stopping monitoring process...
taskkill /f /im python.exe /fi "COMMANDLINE eq *run_monitor.py*" 2>nul

echo.
echo [%date% %time%] Watchdog and monitoring manually stopped >> watchdog.log
echo All processes stopped.
echo.
pause