@echo off
echo ========================================
echo    POSCO 워치햄스터 런처 (Windows)
echo ========================================
echo.

echo 🎯 워치햄스터 메뉴 시스템을 시작합니다...
cd /d "%~dp0"
cd ..\..\..
python -m Monitoring.WatchHamster_Project.scripts.watchhamster_launcher
echo.

echo ========================================
echo 워치햄스터 런처가 종료되었습니다.
echo 문제가 있으면 담당자에게 연락하세요.
echo ========================================
echo.
pause