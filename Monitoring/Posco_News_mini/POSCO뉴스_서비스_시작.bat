@echo off
cd /d "%~dp0"

REM Windows 작업 스케줄러에서 실행할 때 사용
REM 백그라운드에서 조용히 실행됨

echo [%date% %time%] 감시견 서비스 시작 >> watchdog.log

REM 기존 프로세스가 있다면 종료
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_watchdog.py*" 2>nul

REM 감시견 시작 (백그라운드)
start /min python monitor_watchdog.py

echo [%date% %time%] 감시견 서비스 시작 완료 >> watchdog.log