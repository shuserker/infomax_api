@echo off
chcp 65001 > nul
title POSCO 제어 센터 실행기 v2

echo.
echo ============================================================================
echo 🏭 POSCO 제어 센터 실행기 v2 (경로 수정됨)
echo ============================================================================
echo.

echo 📍 현재 경로: %CD%
echo 📍 PowerShell 스크립트를 실행합니다...
echo.

REM 파일 존재 확인
if exist "posco_control_center.ps1" (
    echo ✅ posco_control_center.ps1 파일 발견
) else (
    echo ❌ posco_control_center.ps1 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

if exist "lib_wt_common.ps1" (
    echo ✅ lib_wt_common.ps1 파일 발견
) else (
    echo ❌ lib_wt_common.ps1 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo.
echo 🚀 PowerShell 스크립트 실행 중...

REM PowerShell 실행 정책 확인 및 스크립트 실행
powershell.exe -ExecutionPolicy Bypass -File "posco_control_center.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 스크립트 실행에 실패했습니다. (오류 코드: %ERRORLEVEL%)
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