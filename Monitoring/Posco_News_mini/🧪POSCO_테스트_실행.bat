@echo off
chcp 65001 > nul
title POSCO 테스트 실행 🧪

echo.
echo ========================================
echo    🧪 POSCO 시스템 테스트 실행 🔬
echo ========================================
echo.

cd /d "%~dp0"

echo 📋 테스트 메뉴:
echo.
echo 1. 실시간 뉴스 모니터 테스트
echo 2. 통합 리포트 스케줄러 테스트  
echo 3. 통합 리포트 수동 생성
echo 4. 개별 뉴스 모니터 테스트
echo 5. 시스템 리셋 (주의!)
echo 0. 종료
echo.

set /p choice="선택하세요 (0-5): "

if "%choice%"=="1" goto test_realtime
if "%choice%"=="2" goto test_scheduler
if "%choice%"=="3" goto test_report
if "%choice%"=="4" goto test_individual
if "%choice%"=="5" goto test_reset
if "%choice%"=="0" goto end
goto invalid

:test_realtime
echo.
echo 🧪 실시간 뉴스 모니터 테스트 시작...
python realtime_news_monitor.py test
goto end

:test_scheduler
echo.
echo 🧪 통합 리포트 스케줄러 테스트 시작...
python integrated_report_scheduler.py test
goto end

:test_report
echo.
echo 🧪 통합 리포트 수동 생성 시작...
python integrated_report_builder.py
goto end

:test_individual
echo.
echo 📋 개별 뉴스 모니터 테스트:
echo 1. 환율 모니터
echo 2. 증시 모니터
echo 3. 뉴욕 모니터
echo 4. 마스터 모니터
set /p subchoice="선택하세요 (1-4): "

if "%subchoice%"=="1" python exchange_monitor.py
if "%subchoice%"=="2" python kospi_monitor.py
if "%subchoice%"=="3" python newyork_monitor.py
if "%subchoice%"=="4" python master_news_monitor.py
goto end

:test_reset
echo.
echo ⚠️  시스템 리셋은 모든 데이터를 초기화합니다!
set /p confirm="정말 실행하시겠습니까? (Y/N): "
if /i "%confirm%"=="Y" (
    echo 🔄 시스템 리셋 실행 중...
    python posco_report_system_reset.py
) else (
    echo 취소되었습니다.
)
goto end

:invalid
echo ❌ 잘못된 선택입니다.
goto end

:end
echo.
pause