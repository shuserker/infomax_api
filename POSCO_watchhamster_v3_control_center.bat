@echo off
chcp 65001 > nul
title POSCO 워치햄스터 v3.0 제어센터

echo.
echo ==========================================
echo    POSCO 워치햄스터 v3.0 제어센터
echo ==========================================
echo.

:MENU
echo [1] 워치햄스터 모니터링 시작
echo [2] 웹훅 테스트
echo [3] AI 분석 실행
echo [4] 비즈니스 데이 비교
echo [5] 상태 확인
echo [0] 종료
echo.
set /p choice="선택하세요 (0-5): "

if "%choice%"=="1" goto MONITOR_START
if "%choice%"=="2" goto WEBHOOK_TEST
if "%choice%"=="3" goto AI_ANALYSIS
if "%choice%"=="4" goto BUSINESS_DAY
if "%choice%"=="5" goto STATUS
if "%choice%"=="0" goto EXIT
goto MENU

:MONITOR_START
echo.
echo 워치햄스터 모니터링을 시작합니다...
python recovery_config/watchhamster_monitor.py
goto MENU

:WEBHOOK_TEST
echo.
echo 웹훅 테스트를 실행합니다...
python recovery_config/test_webhook_sender.py
goto MENU

:AI_ANALYSIS
echo.
echo AI 분석을 실행합니다...
python recovery_config/ai_analysis_engine.py
goto MENU

:BUSINESS_DAY
echo.
echo 비즈니스 데이 비교를 실행합니다...
python recovery_config/business_day_comparison_engine.py
goto MENU

:STATUS
echo.
echo 시스템 상태를 확인합니다...
python recovery_config/git_monitor.py --status
goto MENU

:EXIT
echo.
echo 워치햄스터 제어센터를 종료합니다.
pause
exit
