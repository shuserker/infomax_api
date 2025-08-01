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
echo 8. 📋 상세 일일 요약 (제목+본문 비교)
echo 9. 📊 고급 분석 (30일 추이 + 주단위 분석 + 향후 예상)
echo 10. 📦 패키지 강제 재설치
echo 11. 🔧 수동 설치 가이드
echo 12. ❌ 종료
echo.
echo ========================================
set /p "choice=선택하세요 (1-12): "

if "%choice%"=="1" goto start_watchhamster
if "%choice%"=="2" goto stop_watchhamster
if "%choice%"=="3" goto view_logs
if "%choice%"=="4" goto refresh_status
if "%choice%"=="5" goto test_run
if "%choice%"=="6" goto verify_environment
if "%choice%"=="7" goto file_management
if "%choice%"=="8" goto detailed_summary
if "%choice%"=="9" goto advanced_analysis
if "%choice%"=="10" goto force_install_packages
if "%choice%"=="11" goto manual_install_guide
if "%choice%"=="12" goto exit_program
goto main_menu

:start_watchhamster
REM ==========================================
REM 워치햄스터 시작 섹션 (개선됨)
REM ==========================================
cls
echo.
echo ========================================
echo   🚀 워치햄스터 시작
echo ========================================
echo.

REM 현재 BAT 파일 디렉토리로 이동
cd /d "%~dp0"

echo 🔍 환경 검증 중...
echo.

REM Python 설치 확인 (python, python3 모두 체크)
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Python 발견: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Python 발견: python3
    ) else (
        echo ❌ Python이 설치되지 않았습니다!
        echo 💡 Python 3.9+ 설치 후 다시 실행해주세요.
        echo.
        pause
        goto main_menu
    )
)

REM 필요한 모듈 확인 및 자동 설치
echo 📦 의존성 모듈 확인 중...
%PYTHON_CMD% -c "import requests, psutil, json, subprocess, time, os, sys, numpy, pandas, textblob, nltk, sklearn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 필요한 모듈이 설치되지 않았습니다.
    echo 📦 자동으로 모든 패키지를 설치합니다...
    
    echo 🔄 pip 업그레이드 중...
    %PYTHON_CMD% -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    echo 📦 requirements.txt 설치 중 (방법 1)...
    %PYTHON_CMD% -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    if %errorlevel% neq 0 (
        echo ⚠️ 방법 1 실패, 방법 2 시도 중...
        echo 📦 개별 패키지 설치 중...
        %PYTHON_CMD% -m pip install requests --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install psutil --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install numpy --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install pandas --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install textblob --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install nltk --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        %PYTHON_CMD% -m pip install scikit-learn --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
        
        if %errorlevel% neq 0 (
            echo ⚠️ 방법 2 실패, 방법 3 시도 중...
            echo 📦 대체 미러 사용 중...
            %PYTHON_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
            if %errorlevel% neq 0 (
                echo ❌ 모든 설치 시도 실패!
                echo.
                echo 🔍 문제 해결 방법:
                echo 1. 인터넷 연결 확인
                echo 2. 방화벽/프록시 설정 확인
                echo 3. 관리자 권한으로 실행
                echo 4. 수동 설치: %PYTHON_CMD% -m pip install requests psutil numpy
                echo.
                pause
                goto main_menu
            )
        )
    )
    echo ✅ 모든 패키지 설치 완료!
    echo 🔄 설치된 패키지 확인 중...
    %PYTHON_CMD% -c "import requests, psutil, json, subprocess, time, os, sys, numpy, pandas, textblob, nltk, sklearn; print('✅ 모든 모듈 정상 로드됨')"
) else (
    echo ✅ 모든 필수 모듈이 이미 설치되어 있습니다.
)

REM 기존 프로세스 확인 및 정리
echo 🔍 기존 프로세스 확인 중...
tasklist /fi "imagename eq python.exe" 2>nul | find /i "monitor_WatchHamster.py" >nul
if %errorlevel% == 0 (
    echo ⚠️ 이미 실행 중인 워치햄스터가 발견되었습니다.
    echo 🛑 기존 프로세스를 종료합니다...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *monitor_WatchHamster*" 2>nul
    taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster.py*" 2>nul
    timeout /t 3 /nobreak >nul
)

REM 설정 파일 확인
if not exist "config.py" (
    echo ❌ config.py 파일이 없습니다!
    echo 💡 설정 파일을 확인해주세요.
    echo.
    pause
    goto main_menu
)

REM 워치햄스터 스크립트 확인
if not exist "monitor_WatchHamster.py" (
    echo ❌ monitor_WatchHamster.py 파일이 없습니다!
    echo 💡 스크립트 파일을 확인해주세요.
    echo.
    pause
    goto main_menu
)

REM run_monitor.py 테스트 실행 (윈도우 호환성 확인)
echo 🧪 run_monitor.py 테스트 실행 중...
echo 📋 테스트 결과:
%PYTHON_CMD% run_monitor.py 6
set TEST_EXIT_CODE=%errorlevel%
if %TEST_EXIT_CODE% neq 0 (
    echo.
    echo ❌ run_monitor.py 실행 테스트 실패!
    echo 📝 오류 코드: %TEST_EXIT_CODE%
    echo 💡 모니터링 스크립트에 문제가 있습니다.
    echo.
    echo 🔍 문제 해결 방법:
    echo 1. Python 명령 확인: %PYTHON_CMD% --version
    echo 2. 모듈 설치 확인: %PYTHON_CMD% -m pip list ^| findstr requests
    echo 3. 직접 실행 테스트: %PYTHON_CMD% run_monitor.py 6
    echo.
    pause
    goto main_menu
)
echo ✅ run_monitor.py 테스트 성공!

echo ✅ 환경 검증 완료!
echo.
echo 🚀 워치햄스터를 시작합니다...
echo 📊 실시간 상태: https://infomax.dooray.com
echo 📝 로그 파일: WatchHamster.log
echo.
echo 💡 중지하려면 Ctrl+C를 누르거나
echo    메인 메뉴에서 '2. 워치햄스터 중지'를 선택하세요.
echo.

REM 시작 시간 기록
echo %date% %time% ^| 🚀 워치햄스터 시작 (관리자) >> WatchHamster.log

REM 워치햄스터 실행 (에러 처리 강화)
echo 🐹 워치햄스터 실행 중...
%PYTHON_CMD% monitor_WatchHamster.py
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo ❌ 워치햄스터 실행 중 오류가 발생했습니다!
    echo 📝 오류 코드: %EXIT_CODE%
    echo 📋 로그 파일을 확인해주세요: WatchHamster.log
    echo.
    echo %date% %time% ^| ❌ 워치햄스터 오류 종료 (코드: %EXIT_CODE%) >> WatchHamster.log
) else (
    echo.
    echo 🛑 워치햄스터가 정상적으로 중단되었습니다.
    echo %date% %time% ^| 🛑 워치햄스터 정상 중단 (관리자) >> WatchHamster.log
)

echo.
echo 💡 메인 메뉴로 돌아갑니다...
timeout /t 3 /nobreak >nul
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

:detailed_summary
cls
echo.
echo ========================================
echo   📋 상세 일일 요약 (제목+본문 비교)
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 상세 요약 파일 확인 중...

if exist "detailed_daily_summary.json" (
    echo 📋 detailed_daily_summary.json 파일이 존재합니다.
    echo ───────────────────────────────────────
    type "detailed_daily_summary.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 detailed_daily_summary.json 파일이 없습니다.
    echo 💡 워치햄스터가 실행되어야 생성됩니다.
)

echo.
echo �� 파일 관리 옵션:
echo 1. 상세 요약 파일 정리 (오래된 파일 삭제)
echo 2. 뒤로 가기
echo.
set /p "summary_choice=선택하세요 (1-2): "

if "%summary_choice%"=="1" (
    echo 📋 상세 요약 파일을 정리합니다...
    if exist "detailed_daily_summary.json" (
        del "detailed_daily_summary.json"
        echo ✅ 상세 요약 파일이 삭제되었습니다.
    ) else (
        echo 📝 상세 요약 파일이 없습니다.
    )
) else if "%summary_choice%"=="2" (
    goto main_menu
)

echo.
pause
goto detailed_summary

:advanced_analysis
cls
echo.
echo ========================================
echo   📊 고급 분석
echo ========================================
echo.
echo 📊 고급 분석 옵션:
echo 1. 30일 추이 분석 (월별 뉴스 수, 주간 추이)
echo 2. 주단위 분석 (월별 뉴스 수, 주간 추이)
echo 3. 향후 예상 분석 (월별 뉴스 수 예측)
echo 4. 뒤로 가기
echo.
set /p "analysis_choice=선택하세요 (1-4): "

if "%analysis_choice%"=="1" goto advanced_analysis_30day
if "%analysis_choice%"=="2" goto advanced_analysis_weekly
if "%analysis_choice%"=="3" goto advanced_analysis_forecast
if "%analysis_choice%"=="4" goto main_menu

:advanced_analysis_30day
cls
echo.
echo ========================================
echo   📊 30일 추이 분석
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 30일 추이 데이터 확인 중...

if exist "news_trend_30days.json" (
    echo 📋 news_trend_30days.json 파일이 존재합니다.
    echo ───────────────────────────────────────
    type "news_trend_30days.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 news_trend_30days.json 파일이 없습니다.
    echo 💡 워치햄스터가 실행되어야 생성됩니다.
)

echo.
echo 📊 옵션:
echo 1. 30일 추이 파일 정리 (오래된 파일 삭제)
echo 2. 뒤로 가기
echo.
set /p "analysis_30day_choice=선택하세요 (1-2): "

if "%analysis_30day_choice%"=="1" (
    echo 📋 30일 추이 파일을 정리합니다...
    if exist "news_trend_30days.json" (
        del "news_trend_30days.json"
        echo ✅ 30일 추이 파일이 삭제되었습니다.
    ) else (
        echo 📝 30일 추이 파일이 없습니다.
    )
) else if "%analysis_30day_choice%"=="2" (
    goto advanced_analysis
)

echo.
pause
goto advanced_analysis_30day

:advanced_analysis_weekly
cls
echo.
echo ========================================
echo   📊 주단위 분석
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 주단위 데이터 확인 중...

if exist "news_trend_weekly.json" (
    echo 📋 news_trend_weekly.json 파일이 존재합니다.
    echo ───────────────────────────────────────
    type "news_trend_weekly.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 news_trend_weekly.json 파일이 없습니다.
    echo 💡 워치햄스터가 실행되어야 생성됩니다.
)

echo.
echo 📊 옵션:
echo 1. 주단위 파일 정리 (오래된 파일 삭제)
echo 2. 뒤로 가기
echo.
set /p "analysis_weekly_choice=선택하세요 (1-2): "

if "%analysis_weekly_choice%"=="1" (
    echo 📋 주단위 파일을 정리합니다...
    if exist "news_trend_weekly.json" (
        del "news_trend_weekly.json"
        echo ✅ 주단위 파일이 삭제되었습니다.
    ) else (
        echo 📝 주단위 파일이 없습니다.
    )
) else if "%analysis_weekly_choice%"=="2" (
    goto advanced_analysis
)

echo.
pause
goto advanced_analysis_weekly

:advanced_analysis_forecast
cls
echo.
echo ========================================
echo   📊 향후 예상 분석
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 향후 예상 데이터 확인 중...

if exist "news_forecast.json" (
    echo 📋 news_forecast.json 파일이 존재합니다.
    echo ───────────────────────────────────────
    type "news_forecast.json"
    echo ───────────────────────────────────────
) else (
    echo 📝 news_forecast.json 파일이 없습니다.
    echo 💡 워치햄스터가 실행되어야 생성됩니다.
)

echo.
echo 📊 옵션:
echo 1. 향후 예상 파일 정리 (오래된 파일 삭제)
echo 2. 뒤로 가기
echo.
set /p "analysis_forecast_choice=선택하세요 (1-2): "

if "%analysis_forecast_choice%"=="1" (
    echo 📋 향후 예상 파일을 정리합니다...
    if exist "news_forecast.json" (
        del "news_forecast.json"
        echo ✅ 향후 예상 파일이 삭제되었습니다.
    ) else (
        echo 📝 향후 예상 파일이 없습니다.
    )
) else if "%analysis_forecast_choice%"=="2" (
    goto advanced_analysis
)

echo.
pause
goto advanced_analysis_forecast

:force_install_packages
cls
echo.
echo ========================================
echo   📦 패키지 강제 재설치
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 Python 환경 확인 중...

REM Python 설치 확인 (python, python3 모두 체크)
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Python 발견: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Python 발견: python3
    ) else (
        echo ❌ Python이 설치되지 않았습니다!
        echo 💡 Python 3.9+ 설치 후 다시 실행해주세요.
        echo.
        pause
        goto main_menu
    )
)

echo.
echo 📦 현재 설치된 패키지 확인 중...
%PYTHON_CMD% -m pip list

echo.
echo ⚠️ 모든 패키지를 강제로 재설치합니다.
echo 💡 이 작업은 시간이 걸릴 수 있습니다.
echo.
set /p "confirm=계속하시겠습니까? (y/N): "

if /i not "%confirm%"=="y" (
    echo ❌ 취소되었습니다.
    pause
    goto main_menu
)

echo.
echo 🔄 pip 업그레이드 중...
%PYTHON_CMD% -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

echo.
echo 📦 기존 패키지 제거 중...
%PYTHON_CMD% -m pip uninstall -y requests psutil numpy pandas textblob nltk scikit-learn

echo.
echo 📦 requirements.txt 재설치 중 (방법 1)...
%PYTHON_CMD% -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ 방법 1 실패, 방법 2 시도 중...
    echo 📦 개별 패키지 설치를 시도합니다...
    %PYTHON_CMD% -m pip install requests --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install psutil --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install numpy --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install pandas --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install textblob --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install nltk --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    %PYTHON_CMD% -m pip install scikit-learn --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    
    if %errorlevel% neq 0 (
        echo.
        echo ⚠️ 방법 2 실패, 방법 3 시도 중...
        echo 📦 대체 미러 사용 중...
        %PYTHON_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    )
)

echo.
echo 🔄 설치된 패키지 확인 중...
%PYTHON_CMD% -c "import requests, psutil, json, subprocess, time, os, sys, numpy, pandas, textblob, nltk, sklearn; print('✅ 모든 모듈 정상 로드됨')"

if %errorlevel% == 0 (
    echo.
    echo ✅ 패키지 재설치 완료!
    echo 💡 이제 워치햄스터를 실행할 수 있습니다.
) else (
    echo.
    echo ❌ 패키지 재설치 실패!
    echo 💡 인터넷 연결을 확인하고 다시 시도해주세요.
)

echo.
pause
goto main_menu

:manual_install_guide
cls
echo.
echo ========================================
echo   🔧 수동 설치 가이드
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 Python 환경 확인 중...

REM Python 설치 확인 (python, python3 모두 체크)
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Python 발견: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Python 발견: python3
    ) else (
        echo ❌ Python이 설치되지 않았습니다!
        echo 💡 Python 3.9+ 설치 후 다시 실행해주세요.
        echo.
        pause
        goto main_menu
    )
)

echo.
echo 📋 수동 설치 명령어:
echo ========================================
echo.
echo 1️⃣ 기본 패키지 설치:
echo %PYTHON_CMD% -m pip install requests psutil
echo.
echo 2️⃣ 데이터 분석 패키지:
echo %PYTHON_CMD% -m pip install numpy pandas
echo.
echo 3️⃣ 텍스트 처리 패키지:
echo %PYTHON_CMD% -m pip install textblob nltk
echo.
echo 4️⃣ 머신러닝 패키지:
echo %PYTHON_CMD% -m pip install scikit-learn
echo.
echo 5️⃣ 한번에 설치 (권장):
echo %PYTHON_CMD% -m pip install -r requirements.txt
echo.
echo ========================================
echo.
echo 🔧 문제 해결 방법:
echo.
echo ❓ SSL 오류 발생 시:
echo %PYTHON_CMD% -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org requests psutil numpy
echo.
echo ❓ 프록시 환경인 경우:
echo set HTTP_PROXY=http://proxy.company.com:8080
echo set HTTPS_PROXY=http://proxy.company.com:8080
echo %PYTHON_CMD% -m pip install requests psutil numpy
echo.
echo ❓ 관리자 권한 필요 시:
echo 관리자 권한으로 CMD 실행 후 위 명령어 실행
echo.
echo ========================================
echo.
echo 💡 설치 완료 후 메뉴 1번으로 워치햄스터를 시작하세요.
echo.
pause
goto main_menu

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