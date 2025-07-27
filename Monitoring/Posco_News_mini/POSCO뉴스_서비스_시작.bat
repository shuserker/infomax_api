@echo off
cd /d "%~dp0"

REM Windows 작업 스케줄러에서 실행할 때 사용
REM 백그라운드에서 조용히 실행됨

echo [%date% %time%] Watchdog service starting >> watchdog.log

REM Kill existing processes if any
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_watchdog.py*" 2>nul

REM Start watchdog (background)
start /min python monitor_watchdog.py

echo [%date% %time%] Watchdog service started >> watchdog.log