@echo off
chcp 65001 > nul
title 🛑 POSCO 미니뉴스 스마트모니터링 - 중지
color 0C

echo.
echo ========================================
echo   🛑 POSCO 미니뉴스 스마트모니터링 중지
echo ========================================
echo.

cd /d "%~dp0"

echo 🔍 실행 중인 프로세스 확인 중...
echo.

REM 워치햄스터 프로세스 확인
set "found_process=0"
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find /i "monitor_WatchHamster"') do (
    set "found_process=1"
    echo 📋 워치햄스터 프로세스 발견: PID %%i
)

REM 일반 Python 프로세스 확인 (워치햄스터 관련)
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find /i "run_monitor"') do (
    set "found_process=1"
    echo 📋 모니터링 프로세스 발견: PID %%i
)

if "%found_process%"=="0" (
    echo ⚠️ 실행 중인 POSCO 모니터링 프로세스가 없습니다.
    echo 💡 이미 중지되었거나 다른 방법으로 실행 중일 수 있습니다.
) else (
    echo.
    echo 🛑 프로세스 종료 시도 중...
    echo.
    
    REM 워치햄스터 관련 프로세스 종료
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *monitor_WatchHamster*" 2>nul
    taskkill /f /im python.exe /fi "WINDOWTITLE eq *run_monitor*" 2>nul
    
    REM 명령행에서 감지된 프로세스 종료
    wmic process where "commandline like '%%monitor_WatchHamster%%'" call terminate 2>nul
    wmic process where "commandline like '%%run_monitor%%'" call terminate 2>nul
    
    echo ⏳ 프로세스 종료 대기 중...
    timeout /t 3 /nobreak >nul
    
    REM 종료 확인
    set "still_running=0"
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| find /i "monitor_WatchHamster"') do (
        set "still_running=1"
    )
    
    if "%still_running%"=="1" (
        echo ⚠️ 일부 프로세스가 여전히 실행 중입니다.
        echo 💡 관리자 권한으로 다시 실행해보세요.
        echo.
        echo 🔧 강제 종료를 시도합니다...
        taskkill /f /im python.exe 2>nul
        timeout /t 2 /nobreak >nul
    ) else (
        echo ✅ 모든 프로세스가 성공적으로 종료되었습니다.
    )
)

echo.
echo 📝 로그 기록 중...
echo %date% %time% ^| 🛑 워치햄스터 수동 중지 (CMD) >> WatchHamster.log

echo.
echo 🎉 중지 작업 완료!
echo.
echo 💡 다시 시작하려면:
echo    🛡️ 24시간 워치햄스터: POSCO_워치햄스터_시작.bat
echo    🚀 일회성 작업: 🚀일회성작업_실행.bat
echo.
pause