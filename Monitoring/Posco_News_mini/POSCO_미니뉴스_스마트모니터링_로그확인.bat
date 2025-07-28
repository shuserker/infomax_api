@echo off
chcp 65001 > nul
title POSCO 미니뉴스 스마트모니터링 - 로그확인
color 0B

echo.
echo ========================================
echo   📊 POSCO 미니뉴스 스마트모니터링 로그
echo ========================================
echo.

cd /d "%~dp0"

if exist "WatchHamster.log" (
    echo 📊 워치햄스터 로그 (최근 30줄):
    echo ----------------------------------------
    powershell -Command "Get-Content 'WatchHamster.log' -Tail 30"
    echo ----------------------------------------
) else (
    echo 📝 워치햄스터 로그 파일이 없습니다.
)

echo.

if exist "WatchHamster_status.json" (
    echo 📋 현재 상태:
    echo ----------------------------------------
    type "WatchHamster_status.json"
    echo ----------------------------------------
) else (
    echo 📝 상태 파일이 없습니다.
)

echo.
pause