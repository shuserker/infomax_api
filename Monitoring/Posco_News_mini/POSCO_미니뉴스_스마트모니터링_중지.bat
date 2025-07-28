@echo off
chcp 65001 > nul
title POSCO 미니뉴스 스마트모니터링 - 중지
color 0C

echo.
echo ========================================
echo   🛑 POSCO 미니뉴스 스마트모니터링 중지
echo ========================================
echo.
echo 🛑 워치햄스터 프로세스를 중지합니다...
echo.

cd /d "%~dp0"

echo 🔍 Python 프로세스 확인 중...
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if %errorlevel% == 0 (
    echo 📋 Python 프로세스 발견, 종료 시도 중...
    taskkill /f /im python.exe 2>nul
    if %errorlevel% == 0 (
        echo ✅ 프로세스 중지 완료
    ) else (
        echo ⚠️ 프로세스 중지 실패 (관리자 권한이 필요할 수 있습니다)
        echo 💡 관리자 권한으로 다시 실행해보세요
    )
) else (
    echo ⚠️ 실행 중인 Python 프로세스가 없습니다
)

echo.
echo %date% %time% ^| 🛑 워치햄스터 수동 중지 (CMD) >> WatchHamster.log

echo 🎉 중지 완료!
echo.
pause