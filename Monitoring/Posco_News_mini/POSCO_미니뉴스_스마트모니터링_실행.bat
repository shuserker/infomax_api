@echo off
chcp 65001 > nul
title POSCO 미니뉴스 스마트모니터링 - 실행
color 0A

echo.
echo ========================================
echo   🐹 POSCO 미니뉴스 스마트모니터링 실행
echo ========================================
echo.
echo 🚀 워치햄스터를 시작합니다...
echo.

cd /d "%~dp0"
python monitor_WatchHamster.py

echo.
echo 🛑 워치햄스터가 중단되었습니다.
pause