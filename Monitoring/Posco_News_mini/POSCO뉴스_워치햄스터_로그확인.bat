@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo POSCO 뉴스 모니터 - 워치햄스터 🛡️ 로그
echo ========================================

if exist WatchHamster.log (
    echo 📊 워치햄스터 로그 (최근 30줄):
    echo ----------------------------------------
    powershell "Get-Content WatchHamster.log -Tail 30"
    echo ----------------------------------------
) else (
    echo 📝 워치햄스터 로그 파일이 없습니다.
)

echo.
if exist WatchHamster_status.json (
    echo 📋 현재 상태:
    echo ----------------------------------------
    type WatchHamster_status.json
    echo ----------------------------------------
) else (
    echo 📝 상태 파일이 없습니다.
)

echo.
echo 📚 사용 가능한 명령어:
echo - 🚀POSCO뉴스_완전자동화_시작.bat : 완전 자동화 시작
echo - ⏹️POSCO뉴스_완전자동화_중지.bat  : 완전 자동화 중지
echo - 📊POSCO뉴스_워치햄스터_로그확인.bat : 로그 확인
echo.
pause