@echo off
chcp 65001 > nul
title POSCO 미니뉴스 - Git 업데이트
color 0D

echo.
echo ========================================
echo   🔄 POSCO 미니뉴스 Git 업데이트
echo ========================================
echo.

cd /d "%~dp0"

echo ⏹️ 현재 모니터링 중지 중...
call "POSCO_미니뉴스_스마트모니터링_중지.bat"

echo.
echo 📥 Git에서 최신 코드 가져오는 중...
git pull origin main
if %errorlevel% neq 0 (
    echo ❌ Git pull 실패!
    echo 수동으로 확인해주세요.
    pause
    exit /b 1
)

echo ✅ Git pull 성공

echo.
echo 🚀 업데이트 완료! 모니터링 재시작 중...
start "" "POSCO_미니뉴스_스마트모니터링_실행.bat"

echo.
echo ========================================
echo   🎉 업데이트 및 재시작 완료!
echo ========================================
echo.
pause