@echo off
chcp 65001 > nul
title 🐹 워치햄스터 단순 실행

echo.
echo ========================================
echo   🐹 워치햄스터 단순 실행
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 Python 확인 중...
python --version
if %errorlevel% neq 0 (
    echo ❌ python 명령이 없습니다.
    echo 🔍 python3 확인 중...
    python3 --version
    if %errorlevel% neq 0 (
        echo ❌ Python이 설치되지 않았습니다!
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo.
echo ✅ Python 발견: %PYTHON_CMD%
echo.

echo 🧪 run_monitor.py 테스트...
echo 📋 실행 결과:
%PYTHON_CMD% run_monitor.py 6
set TEST_RESULT=%errorlevel%

echo.
if %TEST_RESULT% == 0 (
    echo ✅ run_monitor.py 테스트 성공!
    echo.
    echo 🚀 워치햄스터 시작...
    echo 📋 실행 결과:
    %PYTHON_CMD% monitor_WatchHamster.py
) else (
    echo ❌ run_monitor.py 테스트 실패!
    echo 📝 오류 코드: %TEST_RESULT%
    echo.
    echo 🔍 문제 해결:
    echo 1. Python 버전 확인: %PYTHON_CMD% --version
    echo 2. 모듈 확인: %PYTHON_CMD% -c "import requests, psutil, numpy"
    echo 3. 직접 실행: %PYTHON_CMD% run_monitor.py 6
)

echo.
pause 