@echo off
chcp 65001 > nul
title 🐹 POSCO 미니뉴스 스마트모니터링 - 실행
color 0A

echo.
echo ========================================
echo   🐹 POSCO 미니뉴스 스마트모니터링 실행
echo ========================================
echo.

REM 현재 BAT 파일 디렉토리로 이동
cd /d "%~dp0"

echo 🔍 환경 검증 중...
echo.

REM Python 설치 확인 (python, python3 모두 체크)
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Python 발견: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Python 발견: python3
    ) else (
        echo ❌ Python이 설치되지 않았습니다!
        echo 💡 Python 3.9+ 설치 후 다시 실행해주세요.
        echo.
        pause
        exit /b 1
    )
)

REM 필요한 모듈 확인
echo 📦 의존성 모듈 확인 중...
%PYTHON_CMD% -c "import requests, psutil, json, subprocess, time, os, sys" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 필요한 모듈이 설치되지 않았습니다.
    echo 📦 자동으로 설치를 시도합니다...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 모듈 설치 실패!
        echo 💡 수동으로 'pip install requests psutil' 실행 후 다시 시도해주세요.
        echo.
        pause
        exit /b 1
    )
    echo ✅ 모듈 설치 완료!
)

REM 기존 프로세스 확인 및 정리
echo 🔍 기존 프로세스 확인 중...
tasklist /fi "imagename eq python.exe" 2>nul | find /i "monitor_WatchHamster.py" >nul
if %errorlevel% == 0 (
    echo ⚠️ 이미 실행 중인 워치햄스터가 발견되었습니다.
    echo 🛑 기존 프로세스를 종료합니다...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *monitor_WatchHamster*" 2>nul
    taskkill /f /im python.exe /fi "COMMANDLINE eq *monitor_WatchHamster.py*" 2>nul
    timeout /t 3 /nobreak >nul
)

REM 설정 파일 확인
if not exist "config.py" (
    echo ❌ config.py 파일이 없습니다!
    echo 💡 설정 파일을 확인해주세요.
    echo.
    pause
    exit /b 1
)

REM 워치햄스터 스크립트 확인
if not exist "monitor_WatchHamster.py" (
    echo ❌ monitor_WatchHamster.py 파일이 없습니다!
    echo 💡 스크립트 파일을 확인해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 환경 검증 완료!
echo.
echo 🚀 워치햄스터를 시작합니다...
echo 📊 실시간 상태: https://infomax.dooray.com
echo 📝 로그 파일: WatchHamster.log
echo.
echo 💡 중지하려면 Ctrl+C를 누르거나
echo    'POSCO_미니뉴스_스마트모니터링_중지.bat'를 실행하세요.
echo.

REM 시작 시간 기록
echo %date% %time% ^| 🚀 워치햄스터 시작 (CMD 개선판) >> WatchHamster.log

REM 워치햄스터 실행 (에러 처리 강화)
echo 🐹 워치햄스터 실행 중...
%PYTHON_CMD% monitor_WatchHamster.py
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo ❌ 워치햄스터 실행 중 오류가 발생했습니다!
    echo 📝 오류 코드: %EXIT_CODE%
    echo 📋 로그 파일을 확인해주세요: WatchHamster.log
    echo.
    echo %date% %time% ^| ❌ 워치햄스터 오류 종료 (코드: %EXIT_CODE%) >> WatchHamster.log
) else (
    echo.
    echo 🛑 워치햄스터가 정상적으로 중단되었습니다.
    echo %date% %time% ^| 🛑 워치햄스터 정상 중단 (CMD 개선판) >> WatchHamster.log
)

echo.
echo 💡 다시 시작하려면 이 파일을 다시 실행하세요.
echo.
pause