@echo off
REM ============================================================================
REM Posco Git 업데이트
REM POSCO 시스템 구성요소
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

chcp 65001 > nul
title POSCO Git 업데이트 🔄

echo.
echo ========================================
echo    🔄 POSCO 시스템 Git 업데이트 📥
echo ========================================
echo.

cd /d "%~dp0"
cd ..\..

echo 🔍 현재 Git 상태 확인...
git status

echo.
echo 📥 원격 저장소에서 최신 변경사항 가져오기...
git fetch origin

echo.
echo 🔍 업데이트 가능한 변경사항 확인...
git log HEAD..origin/main --oneline
if errorlevel 1 (
    echo ℹ️  업데이트할 변경사항이 없습니다.
    goto end
)

echo.
echo 📋 업데이트 내용:
git log HEAD..origin/main --pretty=format:"%%h - %%s (%%an, %%ar)"

echo.
echo.
set /p confirm="업데이트를 진행하시겠습니까? (Y/N): "
if /i "%confirm%" neq "Y" (
    echo 취소되었습니다.
    goto end
)

echo.
echo 🛑 실행 중인 모니터링 프로세스 확인...
tasklist | findstr python.exe | findstr -i posco
if not errorlevel 1 (
    echo ⚠️  POSCO 모니터링이 실행 중입니다.
    set /p stop_confirm="모니터링을 중지하고 업데이트하시겠습니까? (Y/N): "
    if /i "%stop_confirm%"=="Y" (
        echo 🛑 모니터링 중지 중...
        taskkill /f /im python.exe 2>nul
        timeout /t 3 /nobreak > nul
    ) else (
        echo 업데이트가 취소되었습니다.
        goto end
    )
)

echo.
echo 📥 Git 업데이트 실행...
git pull origin main --allow-unrelated-histories
if errorlevel 1 (
    echo ❌ Git 업데이트 실패!
    echo 🔧 수동으로 해결이 필요할 수 있습니다.
    goto end
)

echo.
echo ✅ Git 업데이트 완료!

echo.
echo 📦 Python 패키지 업데이트 확인...
cd Monitoring\POSCO News 250808_mini
pip install -r requirements.txt --upgrade --quiet

echo.
echo 🎉 모든 업데이트가 완료되었습니다!
echo 🚀 이제 워치햄스터를 다시 시작할 수 있습니다.

:end
echo.
pause