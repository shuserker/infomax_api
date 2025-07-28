@echo off
echo ========================================
echo POSCO 뉴스 모니터 업데이트 및 재시작
echo ========================================

echo 현재 모니터링 중지 중...
call stop_posco_monitor.bat

echo.
echo Git에서 최신 코드 가져오는 중...
git pull origin main

if %errorlevel% neq 0 (
    echo [ERROR] Git pull 실패! 수동으로 확인해주세요.
    pause
    exit /b 1
)

echo.
echo 업데이트 완료! 모니터링 재시작 중...
call start_posco_monitor.bat

echo.
echo ========================================
echo 업데이트 및 재시작 완료!
echo ========================================
pause