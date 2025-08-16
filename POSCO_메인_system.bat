@echo off
chcp 65001 > nul
title POSCO 메인 시스템 제어센터

echo.
echo ==========================================
echo    POSCO 메인 시스템 제어센터 v3.0
echo ==========================================
echo.

:MENU
echo [1] POSCO 뉴스 모니터링 시작
echo [2] 워치햄스터 모니터링 시작  
echo [3] 전체 시스템 상태 확인
echo [4] 테스트 실행
echo [5] 시스템 종료
echo [0] 종료
echo.
set /p choice="선택하세요 (0-5): "

if "%choice%"=="1" goto NEWS_START
if "%choice%"=="2" goto WATCHHAMSTER_START
if "%choice%"=="3" goto STATUS_CHECK
if "%choice%"=="4" goto TEST_RUN
if "%choice%"=="5" goto SYSTEM_STOP
if "%choice%"=="0" goto EXIT
goto MENU

:NEWS_START
echo.
echo POSCO 뉴스 모니터링을 시작합니다...
python recovery_config/integrated_news_parser.py
goto MENU

:WATCHHAMSTER_START
echo.
echo 워치햄스터 모니터링을 시작합니다...
python recovery_config/watchhamster_monitor.py
goto MENU

:STATUS_CHECK
echo.
echo 시스템 상태를 확인합니다...
python recovery_config/system_status_checker.py
goto MENU

:TEST_RUN
echo.
echo 테스트를 실행합니다...
python -m pytest recovery_config/test_*.py -v
goto MENU

:SYSTEM_STOP
echo.
echo 모든 시스템을 종료합니다...
taskkill /f /im python.exe 2>nul
echo 시스템이 종료되었습니다.
goto MENU

:EXIT
echo.
echo POSCO 시스템을 종료합니다.
pause
exit
