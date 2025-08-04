@echo off
chcp 65001 > nul
title POSCO 워치햄스터 🐹🛡️

echo.
echo ========================================
echo    🐹 POSCO 워치햄스터 시작 🛡️
echo ========================================
echo.
echo 📋 시스템 초기화 중...
echo.

cd /d "%~dp0"

echo 🔍 Python 환경 확인 중...
python --version
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다.
    echo 📥 Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

echo.
echo 📦 필수 패키지 확인 중...
pip install -r requirements.txt --quiet

echo.
echo 🚀 워치햄스터 시작 중...
echo.
echo ⚠️  이 창을 닫지 마세요! 시스템 관리자가 실행 중입니다.
echo 📱 알림: 자동으로 뉴스 모니터링과 리포트 시스템이 시작됩니다.
echo.

python monitor_WatchHamster.py

echo.
echo 🛑 워치햄스터가 종료되었습니다.
pause