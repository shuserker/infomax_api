@echo off
REM ==========================================
REM POSCO 뉴스 모니터링 시스템 - 통합 관리자
REM ==========================================
REM 
REM 모든 모니터링 기능을 통합 관리하는 배치 파일입니다.
REM 
REM 주요 기능:
REM - 워치햄스터 시작/중지
REM - 실시간 로그 확인
REM - 환경 검증 및 테스트
REM - 파일 관리 (로그, 캐시 정리)
REM 
REM 사용법:
REM - 더블클릭으로 실행
REM - 메뉴에서 원하는 기능 선택
REM 
REM 작성자: AI Assistant
REM 최종 수정: 2025-07-28 (최적화)
REM ==========================================

chcp 65001 > nul
title 🚀 POSCO 모니터링 관리자
color 0F

:main_menu
cls
echo.
echo ========================================
echo   🚀 POSCO 모니터링 관리자
echo ========================================
echo.
echo 📊 현재 상태:
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
echo ========================================
echo 📋 관리 메뉴:
echo ========================================
echo.
echo 1. 🚀 워치햄스터 시작 (자동 복구 모드)
echo 2. 🛑 워치햄스터 중지
echo 3. 📊 로그 확인
echo 4. 🔄 상태 새로고침
echo 5. 🧪 테스트 실행 (일회성 체크)
echo 6. ⚙️ 환경 검증
echo 7. 📁 파일 관리
echo 8. ❌ 종료
echo.
echo ========================================
set /p "choice=선택하세요 (1-8): "

if "%choice%"=="1" goto start_watchhamster
if "%choice%"=="2" goto stop_watchhamster
if "%choice%"=="3" goto view_logs
if "%choice%"=="4" goto refresh_status
if "%choice%"=="5" goto test_run
if "%choice%"=="6" goto verify_environment
if "%choice%"=="7" goto file_management
if "%choice%"=="8" goto exit_program
goto main_menu

:start_watchhamster
REM ==========================================
REM 워치햄스터 시작 섹션
REM ==========================================
cls
echo.
echo ========================================
echo   🚀 워치햄스터 시작
echo ========================================
echo.
echo 🔍 환경 검증 중...

cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo 💡 Python 3.9+ 설치 후 다시 실행해주세요.
    echo.
    pause
    goto main_menu
)

REM 의존성 확인
echo 📦 의존성 모듈 확인 중...
python -c "import requests, psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 필요한 모듈이 설치되지 않았습니다.
    echo 📦 자동으로 설치를 시도합니다...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 모듈 설치 실패!
        pause
        goto main_menu
    )
    echo ✅ 모듈 설치 완료!
)

REM 기존 프로세스 정리
if "%watchhamster_running%"=="1" (
    echo ⚠️ 이미 실행 중인 워치햄스터가 있습니다.
    echo 🛑 기존 프로세스를 종료합니다...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *monitor_WatchHamster*" 2>nul
    timeout /t 3 /nobreak >nul
)

echo ✅ 환경 검증 완료!
echo.
echo 🚀 워치햄스터를 시작합니다...
echo %date% %time% ^| 🚀 워치햄스터 시작 (관리자) >> WatchHamster.log

start "🐹 POSCO 워치햄스터" python monitor_WatchHamster.py

echo ✅ 워치햄스터가 백그라운드에서 시작되었습니다.
echo 📊 실시간 상태: https://infomax.dooray.com
echo.
pause
goto main_menu

:stop_watchhamster
cls
echo.
echo ========================================
echo   🛑 워치햄스터 중지
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 프로세스 종료 중...

REM 워치햄스터 관련 프로세스 종료
taskkill /f /im python.exe /fi "WINDOWTITLE eq *monitor_WatchHamster*" 2>nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq *run_monitor*" 2>nul
wmic process where "commandline like '%%monitor_WatchHamster%%'" call terminate 2>nul
wmic process where "commandline like '%%run_monitor%%'" call terminate 2>nul

timeout /t 3 /nobreak >nul

echo %date% %time% ^| 🛑 워치햄스터 중지 (관리자) >> WatchHamster.log
echo ✅ 워치햄스터가 중지되었습니다.
echo.
pause
goto main_menu

:view_logs
cls
echo.
echo ========================================
echo   📊 로그 확인
echo ========================================
echo.

cd /d "%~dp0"

if exist "WatchHamster.log" (
    echo 📊 워치햄스터 로그 (최근 15줄):
    echo ───────────────────────────────────────
    
    REM 간단한 방식: 전체 로그를 표시하되 스크롤 가능하게
    echo 💡 전체 로그를 표시합니다. 스크롤하여 최근 내용을 확인하세요.
    echo.
    type "WatchHamster.log"
    
    echo ───────────────────────────────────────
) else (
    echo 📝 로그 파일이 없습니다.
)

echo.
if exist "WatchHamster_status.json" (
    echo 📋 상태 정보:
    echo ───────────────────────────────────────
    type "WatchHamster_status.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 상태 파일이 없습니다.
)

echo.
pause
goto main_menu

:refresh_status
cls
echo.
echo ========================================
echo   🔄 상태 새로고침
echo ========================================
echo.
echo 🔄 상태를 새로고침합니다...
timeout /t 2 /nobreak >nul
goto main_menu

:test_run
cls
echo.
echo ========================================
echo   🧪 테스트 실행
echo ========================================
echo.
echo 🧪 일회성 뉴스 체크를 실행합니다...

cd /d "%~dp0"
python run_monitor.py 1

echo.
echo ✅ 테스트 완료!
echo.
pause
goto main_menu

:verify_environment
cls
echo.
echo ========================================
echo   ⚙️ 환경 검증
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 환경 검증 중...
echo.

REM Python 버전 확인
echo 📋 Python 버전:
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
) else (
    echo ✅ Python 설치 확인됨
)

echo.

REM 의존성 확인
echo 📦 의존성 모듈 확인:
python -c "import requests; print('✅ requests:', requests.__version__)" 2>nul
python -c "import psutil; print('✅ psutil:', psutil.__version__)" 2>nul

echo.

REM 파일 확인
echo 📁 필수 파일 확인:
if exist "config.py" (
    echo ✅ config.py
) else (
    echo ❌ config.py (없음)
)

if exist "monitor_WatchHamster.py" (
    echo ✅ monitor_WatchHamster.py
) else (
    echo ❌ monitor_WatchHamster.py (없음)
)

if exist "run_monitor.py" (
    echo ✅ run_monitor.py
) else (
    echo ❌ run_monitor.py (없음)
)

echo.
pause
goto main_menu

:file_management
cls
echo.
echo ========================================
echo   📁 파일 관리
echo ========================================
echo.

cd /d "%~dp0"

echo 📁 파일 정보:
echo.

if exist "WatchHamster.log" (
    for %%A in ("WatchHamster.log") do set "log_size=%%~zA"
    set /a "log_size_kb=%log_size%/1024"
    echo 📊 WatchHamster.log: %log_size_kb% KB
) else (
    echo 📊 WatchHamster.log: 없음
)

if exist "posco_news_cache.json" (
    for %%A in ("posco_news_cache.json") do set "cache_size=%%~zA"
    set /a "cache_size_kb=%cache_size%/1024"
    echo 📦 posco_news_cache.json: %cache_size_kb% KB
) else (
    echo 📦 posco_news_cache.json: 없음
)

if exist "WatchHamster_status.json" (
    echo 📋 WatchHamster_status.json: 있음
) else (
    echo 📋 WatchHamster_status.json: 없음
)

echo.
echo 📁 파일 관리 옵션:
echo 1. 로그 파일 정리 (오래된 로그 삭제)
echo 2. 캐시 파일 정리
echo 3. 상태 파일 초기화
echo 4. 뒤로 가기
echo.
set /p "file_choice=선택하세요 (1-4): "

if "%file_choice%"=="1" (
    echo 📊 로그 파일을 정리합니다...
    if exist "WatchHamster.log" (
        del "WatchHamster.log"
        echo ✅ 로그 파일이 삭제되었습니다.
    )
) else if "%file_choice%"=="2" (
    echo 📦 캐시 파일을 정리합니다...
    if exist "posco_news_cache.json" (
        del "posco_news_cache.json"
        echo ✅ 캐시 파일이 삭제되었습니다.
    )
) else if "%file_choice%"=="3" (
    echo 📋 상태 파일을 초기화합니다...
    if exist "WatchHamster_status.json" (
        del "WatchHamster_status.json"
        echo ✅ 상태 파일이 삭제되었습니다.
    )
) else if "%file_choice%"=="4" (
    goto main_menu
)

echo.
pause
goto file_management

:exit_program
cls
echo.
echo ========================================
echo   ❌ 프로그램 종료
echo ========================================
echo.
echo 🎉 POSCO 모니터링 관리자를 종료합니다.
echo.
echo 💡 워치햄스터가 실행 중이라면
echo    자동으로 계속 작동합니다.
echo.
pause
exit 