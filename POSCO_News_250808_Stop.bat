@echo off
chcp 65001 > nul
title POSCO News 250808 중지

echo.
echo ==========================================
echo    POSCO News 250808 모니터링 중지
echo ==========================================
echo.

echo 뉴스 모니터링 시스템을 중지합니다...
echo.

REM Python 프로세스 종료
echo [1/2] 모니터링 프로세스 종료 중...
taskkill /f /im python.exe 2>nul

REM 정리 작업
echo [2/2] 정리 작업 수행 중...
python recovery_config/integrated_news_parser.py --cleanup

echo.
echo POSCO News 모니터링이 중지되었습니다.
pause
