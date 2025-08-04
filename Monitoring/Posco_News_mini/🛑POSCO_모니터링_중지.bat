@echo off
chcp 65001 > nul
title POSCO 모니터링 중지 ⛔

echo.
echo ========================================
echo    🛑 POSCO 모니터링 시스템 중지 ⛔
echo ========================================
echo.

echo 🔍 실행 중인 Python 프로세스 확인 중...
tasklist | findstr python.exe

echo.
echo ⚠️  모든 POSCO 관련 Python 프로세스를 종료합니다.
echo 📋 종료 대상:
echo    - 워치햄스터 (monitor_WatchHamster.py)
echo    - 실시간 뉴스 모니터 (realtime_news_monitor.py)
echo    - 통합 리포트 스케줄러 (integrated_report_scheduler.py)
echo.

set /p confirm="정말 모든 모니터링을 중지하시겠습니까? (Y/N): "
if /i "%confirm%" neq "Y" (
    echo 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo 🛑 Python 프로세스 종료 중...
taskkill /f /im python.exe 2>nul
if errorlevel 1 (
    echo ℹ️  실행 중인 Python 프로세스가 없습니다.
) else (
    echo ✅ 모든 Python 프로세스가 종료되었습니다.
)

echo.
echo 🔍 종료 후 상태 확인...
tasklist | findstr python.exe
if errorlevel 1 (
    echo ✅ 모든 POSCO 모니터링이 완전히 중지되었습니다.
) else (
    echo ⚠️  일부 프로세스가 여전히 실행 중일 수 있습니다.
    echo 📋 작업 관리자에서 수동으로 확인해주세요.
)

echo.
pause