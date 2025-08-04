@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title 🔄 Git 덮어씌우기 도구 - Modern Edition

REM Windows 10/11 ANSI 지원 강화
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

REM 현대적 색상 팔레트
set "ESC="
set "RESET=%ESC%[0m"
set "PRIMARY=%ESC%[38;2;0;120;215m"
set "SUCCESS=%ESC%[38;2;16;124;16m"
set "WARNING=%ESC%[38;2;255;185;0m"
set "ERROR=%ESC%[38;2;196;43;28m"
set "WHITE=%ESC%[38;2;255;255;255m"
set "GRAY=%ESC%[38;2;150;150;150m"
set "LIGHT_GRAY=%ESC%[38;2;200;200;200m"

echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %WHITE%🔄 Git 최신 커밋 덮어씌우기 - Modern Edition%RESET%                        %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %LIGHT_GRAY%Windows 10/11 Terminal Optimized%RESET%                                %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%📊 현재 Git 상태%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %PRIMARY%🔍 현재 변경사항 확인 중...%RESET%
git status --porcelain
echo.

echo %WARNING%⚠️ 최신 커밋에 덮어씌웁니다. 계속하시겠습니까?%RESET%
set /p confirm=%PRIMARY%❯ Y/N: %RESET%
if /i "%confirm%" neq "Y" (
    echo %ERROR%❌ 취소되었습니다.%RESET%
    pause
    exit /b
)
echo.
echo %WHITE%🔄 Git 덮어씌우기 진행%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

echo %PRIMARY%📦 1단계: 변경사항 스테이징...%RESET%
git add .
if %errorlevel% neq 0 (
    echo %ERROR%❌ 스테이징 실패%RESET%
    pause
    exit /b 1
)
echo %SUCCESS%✅ 스테이징 완료%RESET%
echo.

echo %PRIMARY%🔄 2단계: 최신 커밋에 덮어씌우기...%RESET%
git commit --amend --no-edit
if %errorlevel% neq 0 (
    echo %ERROR%❌ 커밋 덮어씌우기 실패%RESET%
    pause
    exit /b 1
)
echo %SUCCESS%✅ 커밋 덮어씌우기 완료%RESET%
echo.

echo %PRIMARY%🚀 3단계: 원격 저장소에 강제 푸시...%RESET%
git push --force-with-lease origin main
if %errorlevel% neq 0 (
    echo %ERROR%❌ 푸시 실패%RESET%
    pause
    exit /b 1
)
echo %SUCCESS%✅ 푸시 완료%RESET%
echo.

echo %SUCCESS%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %SUCCESS%│%RESET% %WHITE%🎉 Git 덮어씌우기 완료!%RESET%                                               %SUCCESS%│%RESET%
echo %SUCCESS%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%📋 최신 커밋 정보%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
git log --oneline -1
echo.

echo %GRAY%🕒 완료 시간: %date% %time%%RESET%
echo.
pause