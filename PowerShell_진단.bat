@echo off
chcp 65001 > nul
title PowerShell 환경 진단

echo ============================================================================
echo 🔍 PowerShell 환경 진단
echo ============================================================================
echo.

echo 📋 PowerShell 버전 확인:
powershell.exe -Command "Get-Host | Select-Object Version"
echo.

echo 📋 실행 정책 확인:
powershell.exe -Command "Get-ExecutionPolicy"
echo.

echo 📋 스크립트 파일 존재 확인:
if exist "posco_control_center.ps1" (
    echo ✅ posco_control_center.ps1 파일이 존재합니다.
) else (
    echo ❌ posco_control_center.ps1 파일을 찾을 수 없습니다.
)
echo.

echo 💡 해결 방법:
echo 1. PowerShell을 관리자 권한으로 실행
echo 2. Set-ExecutionPolicy RemoteSigned -Scope CurrentUser 명령 실행
echo 3. 🎛️POSCO_제어센터_실행.bat 파일 사용
echo.

pause