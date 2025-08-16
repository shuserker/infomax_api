@echo off
REM ============================================================================
REM POSCO News 250808 Direct Start
REM POSCO 시스템 구성요소
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

chcp 65001 > nul
title POSCO 메인 알림 시스템 직접 시작

echo.
echo ============================================================================
echo 🏭 POSCO 메인 알림 시스템 직접 시작
echo ============================================================================
echo.

echo 📍 현재 경로: %CD%
echo.

REM 파일 존재 확인
if exist ".comprehensive_repair_backup/posco_main_notifier.py.backup_20250809_181656" (
    echo ✅ posco_main_notifier.py 파일 발견
) else (
    echo ❌ posco_main_notifier.py 파일을 찾을 수 없습니다.
    echo 📍 현재 경로: %CD%
    echo 📁 파일 목록:
    dir Monitoring\POSCO News 250808_mini\*.py
    pause
    exit /b 1
)

echo.
echo 🚀 POSCO 메인 알림 시스템 시작 중...
echo 🛑 종료하려면 Ctrl+C를 누르세요
echo.

cd Monitoring\POSCO News 250808_mini
python Monitoring/POSCO_News_250808/posco_main_notifier.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 시스템 실행에 실패했습니다. (오류 코드: %ERRORLEVEL%)
    echo 💡 해결 방법:
    echo    1. Python이 설치되어 있는지 확인
    echo    2. 필요한 패키지가 설치되어 있는지 확인 (pip install -r requirements.txt)
    echo    3. config.py 파일의 설정 확인
    echo.
    pause
) else (
    echo.
    echo ✅ 시스템이 정상적으로 종료되었습니다.
)

cd ..\..
pause