@echo off
cd /d "%~dp0"
echo ========================================
echo POSCO 뉴스 모니터 감시견 로그
echo ========================================

if exist watchdog.log (
    echo 📊 감시견 로그 (최근 30줄):
    echo ----------------------------------------
    powershell "Get-Content watchdog.log -Tail 30"
    echo ----------------------------------------
) else (
    echo 📝 감시견 로그 파일이 없습니다.
)

echo.
if exist watchdog_status.json (
    echo 📋 현재 상태:
    echo ----------------------------------------
    type watchdog_status.json
    echo ----------------------------------------
) else (
    echo 📝 상태 파일이 없습니다.
)

echo.
echo 📚 사용 가능한 명령어:
echo - start_watchdog.bat : 감시견 시작
echo - stop_watchdog.bat  : 감시견 중지
echo - view_watchdog_log.bat : 로그 확인
echo.
pause