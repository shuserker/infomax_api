@echo off
chcp 65001 > nul
title 📊 POSCO 미니뉴스 스마트모니터링 - 로그확인
color 0B

echo.
echo ========================================
echo   📊 POSCO 미니뉴스 스마트모니터링 로그
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 시스템 상태 확인 중...
echo.

REM 프로세스 상태 확인
set "watchhamster_running=0"
set "monitor_running=0"

for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find /i "monitor_WatchHamster"') do (
    set "watchhamster_running=1"
    set "watchhamster_pid=%%i"
)

for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find /i "run_monitor"') do (
    set "monitor_running=1"
    set "monitor_pid=%%i"
)

echo 📋 프로세스 상태:
if "%watchhamster_running%"=="1" (
    echo 🟢 워치햄스터: 실행 중 (PID: %watchhamster_pid%)
) else (
    echo 🔴 워치햄스터: 중지됨
)

if "%monitor_running%"=="1" (
    echo 🟢 모니터링: 실행 중 (PID: %monitor_pid%)
) else (
    echo 🔴 모니터링: 중지됨
)

echo.

REM 워치햄스터 로그 확인 (순수 배치 파일 방식)
if exist "WatchHamster.log" (
    echo 📊 워치햄스터 로그 (최근 20줄):
    echo ───────────────────────────────────────
    
    REM 간단한 방식: 전체 로그를 표시하되 스크롤 가능하게
    echo 💡 전체 로그를 표시합니다. 스크롤하여 최근 내용을 확인하세요.
    echo.
    type "WatchHamster.log"
    
    echo ───────────────────────────────────────
    
    REM 로그 파일 크기 확인
    for %%A in ("WatchHamster.log") do set "log_size=%%~zA"
    set /a "log_size_kb=%log_size%/1024"
    echo 📏 로그 파일 크기: %log_size_kb% KB
) else (
    echo 📝 워치햄스터 로그 파일이 없습니다.
)

echo.

REM 상태 파일 확인
if exist "WatchHamster_status.json" (
    echo 📋 현재 상태 정보:
    echo ───────────────────────────────────────
    type "WatchHamster_status.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 상태 파일이 없습니다.
)

echo.

REM 캐시 파일 확인
if exist "posco_news_cache.json" (
    echo 📦 캐시 파일 정보:
    for %%A in ("posco_news_cache.json") do set "cache_size=%%~zA"
    set /a "cache_size_kb=%cache_size%/1024"
    echo 📏 캐시 파일 크기: %cache_size_kb% KB
    
    for %%A in ("posco_news_cache.json") do set "cache_date=%%~tA"
    echo 📅 마지막 업데이트: %cache_date%
) else (
    echo 📝 캐시 파일이 없습니다.
)

echo.

REM 실시간 모니터링 옵션
echo 🔄 실시간 모니터링 옵션:
echo 1. 실시간 로그 모니터링 (5초마다 갱신)
echo 2. 프로세스 상태만 확인
echo 3. 종료
echo.
set /p "choice=선택하세요 (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🔄 실시간 로그 모니터링 시작 (종료하려면 Ctrl+C)
    echo ───────────────────────────────────────
    :monitor_loop
    cls
    echo 📊 실시간 로그 모니터링 - %date% %time%
    echo ───────────────────────────────────────
    if exist "WatchHamster.log" (
        echo 💡 전체 로그를 표시합니다. 스크롤하여 최근 내용을 확인하세요.
        echo.
        type "WatchHamster.log"
    ) else (
        echo 로그 파일이 없습니다.
    )
    echo ───────────────────────────────────────
    echo 💡 종료하려면 Ctrl+C를 누르세요.
    timeout /t 5 /nobreak >nul
    goto monitor_loop
) else if "%choice%"=="2" (
    echo.
    echo 📋 프로세스 상태:
    tasklist /fi "imagename eq python.exe" /fo table | find /i "python"
    echo.
    pause
) else (
    echo 종료합니다.
)

echo.
pause