@echo off
REM ============================================================================
REM Posco 제어센터 실행
REM POSCO 시스템 제어센터
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

chcp 65001 > nul
title POSCO 제어 센터 실행기

echo.
echo ============================================================================
echo 🏭 POSCO 제어 센터 실행기
echo ============================================================================
echo.

echo 📍 PowerShell 스크립트를 실행합니다...
echo.

REM PowerShell 실행 정책 확인 및 스크립트 실행
powershell.exe -ExecutionPolicy Bypass -File "posco_control_center.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 스크립트 실행에 실패했습니다.
    echo 💡 해결 방법:
    echo    1. PowerShell을 관리자 권한으로 실행
    echo    2. Set-ExecutionPolicy RemoteSigned 명령 실행
    echo    3. 다시 시도
    echo.
    pause
) else (
    echo.
    echo ✅ 스크립트 실행이 완료되었습니다.
)

pause