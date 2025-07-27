@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo POSCO 뉴스 모니터 - 완전 자동화 시작
echo ========================================
echo.
echo 🐹 워치햄스터 🛡️ 기능:
echo - 모니터링 프로세스 자동 감시
echo - Git 업데이트 자동 체크 (1시간 간격)
echo - 프로세스 오류 시 자동 재시작
echo - 상태 알림 전송
echo.
echo 중단하려면 Ctrl+C를 누르세요
echo.

python monitor_WatchHamster.py

echo.
echo 워치햄스터 🛡️가 중단되었습니다.
pause