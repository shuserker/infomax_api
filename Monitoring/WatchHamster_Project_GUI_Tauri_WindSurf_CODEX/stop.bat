@echo off
chcp 65001 >nul
title WatchHamster 중지

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  ⏹️  WatchHamster 중지                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🛑 WatchHamster 관련 프로세스를 중지합니다...

:: Node.js 프로세스 중지
echo 🔧 Node.js 프로세스 중지 중...
taskkill /f /im node.exe >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Node.js 프로세스 중지됨
) else (
    echo ℹ️  실행 중인 Node.js 프로세스가 없습니다
)

:: Python 프로세스 중지
echo 🐍 Python 프로세스 중지 중...
taskkill /f /im python.exe >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python 프로세스 중지됨
) else (
    echo ℹ️  실행 중인 Python 프로세스가 없습니다
)

:: 포트 확인
echo 🔍 포트 사용 상태 확인 중...
netstat -an | findstr :1420 >nul 2>&1
if %errorLevel% == 0 (
    echo ⚠️  포트 1420이 여전히 사용 중입니다
) else (
    echo ✅ 포트 1420 해제됨
)

netstat -an | findstr :8000 >nul 2>&1
if %errorLevel% == 0 (
    echo ⚠️  포트 8000이 여전히 사용 중입니다
) else (
    echo ✅ 포트 8000 해제됨
)

echo.
echo ✅ WatchHamster가 중지되었습니다!
echo.

timeout /t 3 >nul