@echo off
cd /d "%~dp0"

REM Windows 작업 스케줄러에서 실행할 때 사용
REM 백그라운드에서 조용히 실행됨

echo [%date% %time%] WatchHamster service starting >> WatchHamster.log

REM Kill existing processes if any
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster.py*" 2>nul

REM Start WatchHamster (background)
start /min python monitor_WatchHamster.py

echo [%date% %time%] WatchHamster service started >> WatchHamster.log