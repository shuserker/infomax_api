@echo off
chcp 65001 >nul
echo ========================================
echo POSCO 뉴스 모니터 - 완전 자동화 중지
echo ========================================

echo 워치햄스터 🛡️ 프로세스를 중지합니다...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *watchdog*" 2>nul
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster.py*" 2>nul

echo.
echo 모니터링 프로세스도 중지합니다...
taskkill /f /im python.exe /fi "COMMANDLINE eq *run_monitor.py*" 2>nul

echo.
echo [%date% %time%] 워치햄스터 및 모니터링 수동 중지 >> WatchHamster.log
echo 모든 프로세스가 중지되었습니다.
echo.
pause