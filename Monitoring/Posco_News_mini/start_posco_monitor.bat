@echo off
cd /d "%~dp0"
echo [%date% %time%] POSCO 뉴스 모니터링 시작 >> monitor.log
python run_monitor.py 3 >> monitor.log 2>&1
echo [%date% %time%] POSCO 뉴스 모니터링 종료 >> monitor.log
pause