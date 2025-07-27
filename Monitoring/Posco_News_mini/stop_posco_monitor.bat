@echo off
echo POSCO 뉴스 모니터링 프로세스를 중지합니다...
taskkill /f /im python.exe /fi "WINDOWTITLE eq POSCO*"
echo [%date% %time%] 모니터링 수동 중지 >> monitor.log
echo 모니터링이 중지되었습니다.
pause