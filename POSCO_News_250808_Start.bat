@echo off
chcp 65001 > nul
title POSCO News 250808 시작

echo.
echo ==========================================
echo    POSCO News 250808 모니터링 시작
echo ==========================================
echo.

echo 뉴스 모니터링 시스템을 시작합니다...
echo.

REM API 연결 테스트
echo [1/4] API 연결 상태 확인 중...
python recovery_config/api_connection_manager.py --test

REM 뉴스 파서 초기화
echo [2/4] 뉴스 파서 초기화 중...
python recovery_config/integrated_news_parser.py --init

REM 웹훅 연결 테스트
echo [3/4] 웹훅 연결 테스트 중...
python recovery_config/webhook_sender.py --test

REM 모니터링 시작
echo [4/4] 모니터링 시작...
python recovery_config/integrated_news_parser.py --monitor

echo.
echo POSCO News 모니터링이 시작되었습니다.
echo 종료하려면 POSCO_News_250808_Stop.bat을 실행하세요.
pause
