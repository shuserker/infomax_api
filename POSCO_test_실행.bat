@echo off
chcp 65001 > nul
title POSCO 테스트 실행

echo.
echo ==========================================
echo    POSCO 시스템 테스트 실행
echo ==========================================
echo.

echo 전체 시스템 테스트를 실행합니다...
echo.

REM 환경 설정 테스트
echo [1/6] 환경 설정 테스트...
python recovery_config/test_environment_setup.py

REM API 모듈 테스트
echo [2/6] API 모듈 테스트...
python recovery_config/test_api_modules.py

REM 뉴스 파서 테스트
echo [3/6] 뉴스 파서 테스트...
python recovery_config/test_news_parsers.py

REM 웹훅 전송 테스트
echo [4/6] 웹훅 전송 테스트...
python recovery_config/test_webhook_sender.py

REM 모니터링 시스템 테스트
echo [5/6] 모니터링 시스템 테스트...
python recovery_config/test_watchhamster_monitor.py

REM 통합 테스트
echo [6/6] 통합 테스트...
python -m pytest recovery_config/ -v

echo.
echo 모든 테스트가 완료되었습니다.
pause
