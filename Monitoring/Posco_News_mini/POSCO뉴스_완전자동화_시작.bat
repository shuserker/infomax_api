@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo POSCO News Monitor - Complete Automation
echo ========================================
echo.
echo WatchHamster Functions:
echo - Auto monitoring process supervision
echo - Git update check (1 hour interval)
echo - Auto restart on process error
echo - Status notification
echo.
echo Press Ctrl+C to stop
echo.

python monitor_WatchHamster.py

echo.
echo WatchHamster stopped.
pause