@echo off
REM ==========================================
REM POSCO 뉴스 워치햄스터 시작 (최적화됨)
REM ==========================================
REM 
REM 워치햄스터를 시작하는 통합 스크립트입니다.
REM 자동으로 환경을 검증하고 워치햄스터를 실행합니다.
REM 
REM 사용법: 더블클릭으로 실행
REM 
REM 최종 수정: 2025-07-29 (최적화)
REM ==========================================

chcp 65001 > nul
title 🐹 POSCO 워치햄스터 시작
color 0A

cls
echo.
echo ========================================
echo   🐹 POSCO 워치햄스터 시작
echo ========================================
echo.

cd /d "%~dp0"

REM Python 환경 확인
echo 🔍 Python 환경 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo 💡 Python 3.9 이상을 설치해주세요.
    pause
    exit /b 1
)

REM 의존성 확인
echo 🔍 의존성 확인 중...
python -c "import requests, psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 필요한 모듈이 없습니다. 자동 설치 중...
    pip install requests psutil
)

REM 기존 프로세스 확인
echo 🔍 기존 워치햄스터 프로세스 확인 중...
tasklist /fi "imagename eq python.exe" | find "monitor_WatchHamster" >nul
if %errorlevel% equ 0 (
    echo ⚠️ 워치햄스터가 이미 실행 중입니다.
    echo 🛑 기존 프로세스를 종료하고 새로 시작합니다.
    taskkill /f /im python.exe /fi "windowtitle eq*WatchHamster*" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM 워치햄스터 시작
echo.
echo 🚀 워치햄스터 시작 중...
echo 💡 중단하려면 Ctrl+C를 누르거나 창을 닫으세요.
echo.

python monitor_WatchHamster.py

REM 종료 처리
echo.
echo 🛑 워치햄스터가 종료되었습니다.
pause