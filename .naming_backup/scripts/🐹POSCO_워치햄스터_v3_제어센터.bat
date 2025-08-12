@echo off
chcp 65001 >nul
title 🐹 POSCO WatchHamster v3.0.0 통합 제어센터

:: 색상 설정
color 0A

echo.
echo ================================================================================
echo                    🐹 POSCO WatchHamster v3.0.0 통합 제어센터 🎛️
echo ================================================================================
echo.
echo 🎯 WatchHamster v3.0.0이 모든 POSCO 모니터링 시스템을 통합 관리합니다
echo.

:MAIN_MENU
echo.
echo 🐹 워치햄스터 제어 메뉴를 선택하세요:
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │                           🐹 WatchHamster v3.0.0 통합 관리                        │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │  1. 🚀 워치햄스터 시작        - 전체 모니터링 시스템 시작                    │
echo │  2. 🛑 워치햄스터 중지        - 전체 모니터링 시스템 중지                    │
echo │  3. 🔄 워치햄스터 재시작      - 전체 모니터링 시스템 재시작                  │
echo │  4. 📊 WatchHamster v3.0 상태        - 전체 시스템 상태 확인                        │
echo │  5. 🔧 모듈 관리             - 개별 모듈 상태 및 제어                        │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │                              📰 뉴스 관리                                   │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │  A. 📋 뉴스 로그 확인         - 최신 뉴스 로그 확인                          │
echo │  B. 📈 뉴스 통계 보기         - 뉴스 수집 통계 확인                          │
echo │  C. 🔍 뉴스 검색             - 특정 키워드 뉴스 검색                         │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │                              ⚙️ 고급 옵션                                   │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │  D. 🔧 시스템 진단           - POSCO 시스템 상태 진단                        │
echo │  E. 🧪 시스템 테스트         - 모니터링 시스템 테스트                        │
echo │  F. 📦 데이터 백업           - 뉴스 데이터 백업                              │
echo │  G. 🚀 v3.0 성능 모니터링    - 실시간 성능 분석                             │
echo │  H. 📊 최적화 보고서         - 시스템 최적화 권장사항                        │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 0. ❌ 종료
echo.

:: 시스템 정보 표시
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 💻 시스템 정보: Windows %OS% ^| 시간: %DATE% %TIME:~0,8%                    │
echo │ 📁 작업 디렉토리: %CD%                                                       │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.

set /p choice="🎯 선택하세요 (1-5, A-H, 0): "

if "%choice%"=="1" goto START_WATCHHAMSTER
if "%choice%"=="2" goto STOP_WATCHHAMSTER
if "%choice%"=="3" goto RESTART_WATCHHAMSTER
if "%choice%"=="4" goto CHECK_STATUS
if "%choice%"=="5" goto MANAGE_MODULES
if /i "%choice%"=="A" goto VIEW_NEWS_LOGS
if /i "%choice%"=="B" goto VIEW_NEWS_STATS
if /i "%choice%"=="C" goto SEARCH_NEWS
if /i "%choice%"=="D" goto SYSTEM_DIAGNOSIS
if /i "%choice%"=="E" goto SYSTEM_TEST
if /i "%choice%"=="F" goto BACKUP_DATA
if /i "%choice%"=="G" goto PERFORMANCE_MONITOR
if /i "%choice%"=="H" goto OPTIMIZATION_REPORT
if "%choice%"=="0" goto EXIT
goto INVALID_CHOICE

:START_WATCHHAMSTER
cls
echo.
echo 🚀 WatchHamster v3.0 시작 중...
echo ================================================================================
echo.
echo 🔍 시스템 환경 체크 중...

:: Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 💡 Python 3.7 이상을 설치해주세요.
    pause
    goto MAIN_MENU
)
echo ✅ Python 환경 확인 완료

:: 워치햄스터 스크립트 확인
if not exist ".naming_backup/config_data_backup/watchhamster.log" (
    echo ❌ 워치햄스터 스크립트를 찾을 수 없습니다.
    echo 📁 경로: %CD%\Monitoring\POSCO News 250808_mini\monitor_WatchHamster.py
    pause
    goto MAIN_MENU
)
echo ✅ 워치햄스터 스크립트 확인 완료

echo.
echo 🧹 기존 프로세스 정리 중...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *WatchHamster*" >nul 2>&1
timeout /t 2 >nul

echo.
echo 🐹 WatchHamster v3.0 시작 중...
cd /d "Monitoring\POSCO News 250808_mini"
start "POSCO WatchHamster v3.0" python .naming_backup/config_data_backup/watchhamster.log
cd /d "%~dp0"

echo.
echo ⏳ 시스템 초기화 대기 중 (10초)...
timeout /t 10 >nul

echo.
echo ✅ WatchHamster v3.0 시작되었습니다!
echo 🎉 v3.0 혁신 기능들이 활성화되었습니다:
echo   • 3단계 지능적 복구 시스템
echo   • 실시간 성능 모니터링
echo   • 향상된 알림 시스템
echo   • 자동 최적화 기능
echo.
pause
goto MAIN_MENU:STOP
_WATCHHAMSTER
cls
echo.
echo 🛑 WatchHamster v3.0.0 중지 중...
echo ================================================================================
echo.
echo 🛑 워치햄스터 프로세스 중지 중...

:: 워치햄스터 관련 프로세스 종료
taskkill /f /im python.exe /fi "WINDOWTITLE eq *WatchHamster*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *posco_main_notifier*" >nul 2>&1

timeout /t 3 >nul

echo ✅ 모든 워치햄스터 프로세스가 성공적으로 중지되었습니다.
echo.
pause
goto MAIN_MENU

:RESTART_WATCHHAMSTER
cls
echo.
echo 🔄 WatchHamster v3.0 시작 중...
echo ================================================================================
echo.
call :STOP_WATCHHAMSTER_SILENT
timeout /t 2 >nul
call :START_WATCHHAMSTER_SILENT
echo ✅ WatchHamster v3.0 시작 완료!
echo.
pause
goto MAIN_MENU

:CHECK_STATUS
cls
echo.
echo 📊 WatchHamster v3.0.0 상태 확인
echo ================================================================================
echo.

:: 워치햄스터 프로세스 확인
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq *WatchHamster*" /fo table >nul 2>&1
if errorlevel 1 (
    echo ❌ 워치햄스터가 실행되지 않고 있습니다.
    echo 💡 워치햄스터를 먼저 시작해주세요.
) else (
    echo ✅ WatchHamster v3.0.0이 실행 중입니다.
    echo.
    echo 📊 관리 중인 모듈 상태:
    echo   • 메인 알림 시스템: 실행 중
    echo   • 실시간 뉴스 모니터: 실행 중  
    echo   • 통합 리포트 스케줄러: 실행 중
    echo   • v3.0 성능 모니터: 실행 중
    echo.
    echo 🎯 v3.0 혁신 기능 상태:
    echo   • 3단계 지능적 복구: ✅ 활성화
    echo   • 실시간 성능 모니터링: ✅ 활성화
    echo   • AI 기반 최적화: ✅ 활성화
    echo   • 하이브리드 아키텍처: ✅ 활성화
)

echo.
pause
goto MAIN_MENU

:PERFORMANCE_MONITOR
cls
echo.
echo 🚀 POSCO WatchHamster v3.0.0 성능 모니터링
echo ================================================================================
echo.
echo 📊 실시간 성능 분석을 시작합니다...
echo.

if exist "demo_performance_monitoring.py" (
    echo 🎯 v3.0 성능 모니터링 데모 실행 중...
    python demo_performance_monitoring.py
    echo.
    echo ✅ 성능 모니터링 완료!
) else (
    echo ❌ 성능 모니터링 스크립트를 찾을 수 없습니다.
    echo 📁 파일: demo_performance_monitoring.py
)

echo.
pause
goto MAIN_MENU

:OPTIMIZATION_REPORT
cls
echo.
echo 📊 시스템 최적화 보고서 생성
echo ================================================================================
echo.
echo 🔍 시스템 분석 및 최적화 권장사항 생성 중...
echo.

if exist "system_optimization_report_generator.py" (
    echo 🎯 v3.0 최적화 분석 실행 중...
    python system_optimization_report_generator.py
    echo.
    echo ✅ 최적화 보고서 생성 완료!
    echo 📄 보고서 파일: system_optimization_report.md
) else (
    echo ❌ 최적화 보고서 생성기를 찾을 수 없습니다.
    echo 📁 파일: system_optimization_report_generator.py
)

echo.
pause
goto MAIN_MENU

:SYSTEM_TEST
cls
echo.
echo 🧪 POSCO WatchHamster v3.0.0 시스템 테스트
echo ================================================================================
echo.
echo 🔍 종합 시스템 테스트를 실행합니다...
echo.

if exist "run_comprehensive_tests.py" (
    echo 🎯 v3.0 종합 테스트 실행 중...
    python run_comprehensive_tests.py
    echo.
    echo ✅ 시스템 테스트 완료!
) else (
    echo ❌ 종합 테스트 스크립트를 찾을 수 없습니다.
    echo 📁 파일: run_comprehensive_tests.py
)

echo.
pause
goto MAIN_MENU

:VIEW_NEWS_LOGS
cls
echo.
echo 📋 뉴스 로그 확인
echo ================================================================================
echo.
if exist ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_monitor.log" (
    echo 📄 최근 20줄의 로그:
    echo.
    powershell "Get-Content '.naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_monitor.log' -Tail 20"
) else (
    echo ❌ 로그 파일이 없습니다.
    echo 📁 파일: posco_monitor.log
)
echo.
pause
goto MAIN_MENU

:INVALID_CHOICE
echo.
echo ❌ 잘못된 선택입니다. 다시 시도해주세요.
timeout /t 2 >nul
goto MAIN_MENU

:EXIT
cls
echo.
echo 👋 POSCO WatchHamster v3.0.0 제어센터를 종료합니다.
echo.
echo 🎉 v3.0 혁신적 모니터링 시스템을 이용해주셔서 감사합니다!
echo.
pause
exit /b 0

:: 내부 함수들
:STOP_WATCHHAMSTER_SILENT
taskkill /f /im python.exe /fi "WINDOWTITLE eq *WatchHamster*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster*" >nul 2>&1
goto :eof

:START_WATCHHAMSTER_SILENT
cd /d "Monitoring\POSCO News 250808_mini"
start "POSCO WatchHamster v3.0" python .naming_backup/config_data_backup/watchhamster.log
cd /d "%~dp0"
goto :eof