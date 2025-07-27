@echo off
cd /d "%~dp0"
echo ========================================
echo POSCO 뉴스 모니터링 로그 (최근 50줄)
echo ========================================
if exist monitor.log (
    powershell "Get-Content monitor.log -Tail 50"
) else (
    echo 로그 파일이 없습니다.
)
echo.
echo ========================================
echo 실시간 로그 보기: tail -f monitor.log
echo 모니터링 중지: Ctrl+C 후 작업관리자에서 python.exe 종료
echo ========================================
pause