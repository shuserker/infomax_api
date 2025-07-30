@echo off
chcp 65001 > nul
title POSCO News mini 수동 실행

echo.
echo ========================================
echo   POSCO News mini 수동 실행
echo ========================================
echo.

cd /d "%~dp0"

echo Python 확인 중...
python --version
if %errorlevel% neq 0 (
    echo python 명령이 없습니다.
    echo python3 확인 중...
    python3 --version
    if %errorlevel% neq 0 (
        echo Python이 설치되지 않았습니다!
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo.
echo Python 발견: %PYTHON_CMD%
echo.

echo ========================================
echo   실행할 기능을 선택하세요:
echo ========================================
echo 1. 현재 상태 체크 (변경사항 없어도 상태 알림)
echo 2. 영업일 비교 체크 (현재 vs 직전 영업일 상세 비교)
echo 3. 스마트 모니터링 (뉴스 발행 패턴 기반 적응형)
echo 4. 기본 모니터링 (60분 간격 무한실행)
echo 5. 일일 요약 리포트 (오늘 발행 뉴스 요약)
echo 6. 테스트 알림 전송
echo 7. 상세 일일 요약 (제목 + 본문 비교)
echo 8. 고급 분석 (30일 추이 + 주단위 분석 + 향후 예상)
echo.
set /p choice="선택 (1-8): "

echo.
echo POSCO News mini 시작...
echo 실행 결과:
%PYTHON_CMD% run_monitor.py %choice%

echo.
pause 