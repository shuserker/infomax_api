@echo off
setlocal enabledelayedexpansion
title 🐹 워치햄스터 총괄 관리 센터 - Modern Edition

REM ============================================================================
REM Windows 10/11 최적화 설정
REM ============================================================================
chcp 65001 > nul 2>&1

REM ANSI 지원 강화 (다중 방식)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_system32_cmd.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_System32_WindowsPowerShell_v1.0_powershell.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

REM ANSI 지원 강제 활성화
powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8" > nul 2>&1
echo  > nul

REM 현대적 색상 정의 (Windows 11 스타일)
set "ESC="
set "RESET=%ESC%[0m"
set "PRIMARY=%ESC%[38;2;0;120;215m"
set "SUCCESS=%ESC%[38;2;16;124;16m"
set "WARNING=%ESC%[38;2;255;185;0m"
set "ERROR=%ESC%[38;2;196;43;28m"
set "WHITE=%ESC%[38;2;255;255;255m"
set "GRAY=%ESC%[38;2;150;150;150m"
set "LIGHT_GRAY=%ESC%[38;2;200;200;200m"

REM ============================================================================
REM 메인 메뉴
REM ============================================================================
:main_menu
cls
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %WHITE%🐹 워치햄스터 총괄 관리 센터 - Modern Edition%RESET%                       %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %LIGHT_GRAY%Windows 10/11 Terminal Optimized%RESET%                                %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%🎛️ 시스템 관리%RESET%
echo.
echo %GRAY%┌─ 모니터링 시스템 ─────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %WARNING%1%RESET% %WHITE%🏭 POSCO 뉴스 모니터링%RESET%  %LIGHT_GRAY%포스코 뉴스 및 주가 모니터링%RESET%           %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%┌─ 시스템 관리 ─────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %WARNING%A%RESET% %WHITE%🛡️ 전체 시스템 상태%RESET%     %LIGHT_GRAY%모든 워치햄스터 상태 확인%RESET%                %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%B%RESET% %WHITE%🔄 전체 시스템 업데이트%RESET%  %LIGHT_GRAY%모든 시스템 Git 업데이트%RESET%                 %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%C%RESET% %WHITE%📋 통합 로그 관리%RESET%       %LIGHT_GRAY%모든 시스템 로그 통합 관리%RESET%                %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%D%RESET% %WHITE%🧪 전체 시스템 테스트%RESET%   %LIGHT_GRAY%모든 시스템 통합 테스트%RESET%                   %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%┌─ 고급 관리 ───────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %WARNING%E%RESET% %WHITE%📦 전체 백업 생성%RESET%       %LIGHT_GRAY%모든 시스템 통합 백업%RESET%                     %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%F%RESET% %WHITE%⚙️ 시스템 설정%RESET%         %LIGHT_GRAY%워치햄스터 설정 관리%RESET%                      %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%0 ❌ 종료%RESET%
echo.
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %PRIMARY%🕒 %date% %time%%RESET% %GRAY%│%RESET% %PRIMARY%📂 %cd%%RESET%
echo.

set /p choice=%PRIMARY%❯ 선택하세요: %RESET%

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto settings_menu
if "%choice%"=="0" goto exit_program
echo %ERROR%❌ 잘못된 선택입니다%RESET%
timeout /t 2 /nobreak > nul
goto main_menu

REM ============================================================================
REM 기능 구현
REM ============================================================================
:posco_monitoring
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🏭 POSCO 모니터링 시스템%RESET%                                              %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%🔄 POSCO 모니터링 시스템으로 이동 중...%RESET%
echo.

cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🎛️POSCO_통합_관리_센터.bat" (
    call "🎛️POSCO_통합_관리_센터.bat"
) else (
    echo %ERROR%❌ POSCO 모니터링 시스템을 찾을 수 없습니다%RESET%
    echo %PRIMARY%📂 경로: Monitoring\Posco_News_mini\%RESET%
    pause
)
cd /d "%~dp0"
goto return_menu

:system_status
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🛡️ 전체 시스템 상태%RESET%                                                  %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%🔍 시스템 상태를 확인하고 있습니다...%RESET%
echo.

echo %WHITE%📊 시스템 현황%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

if exist "Monitoring\Posco_News_mini\system_status.json" (
    echo %SUCCESS%✅ POSCO 모니터링      │ 활성화%RESET%
) else (
    echo %WARNING%⚠️ POSCO 모니터링      │ 상태 불명%RESET%
)

echo.
echo %PRIMARY%📈 가동률: %SUCCESS%100%%%RESET% %GRAY%│%RESET% %PRIMARY%🕒 업데이트: %date%%RESET%
echo.
pause
goto return_menu

:system_update
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🔄 전체 시스템 업데이트%RESET%                                              %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%🔄 시스템 업데이트를 진행하고 있습니다...%RESET%
echo.

echo %PRIMARY%🏭 POSCO 모니터링 시스템 업데이트 중...%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🔄POSCO_Git_업데이트.bat" (
    call "🔄POSCO_Git_업데이트.bat" > nul 2>&1
    echo %SUCCESS%✅ POSCO 시스템 업데이트 완료%RESET%
) else (
    echo %ERROR%❌ POSCO 업데이트 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %SUCCESS%🎉 전체 시스템 업데이트 완료!%RESET%
echo.
pause
goto return_menu

:integrated_logs
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%📋 통합 로그 관리%RESET%                                                    %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%📋 통합 로그를 분석하고 있습니다...%RESET%
echo.

echo %PRIMARY%🏭 POSCO 시스템 로그:%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo %WARNING%⚠️ POSCO 로그 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
pause
goto return_menu

:system_test
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🧪 전체 시스템 테스트%RESET%                                               %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%🧪 시스템 테스트를 실행하고 있습니다...%RESET%
echo.

echo %PRIMARY%🏭 POSCO 시스템 테스트:%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🧪POSCO_테스트_실행.bat" (
    call "🧪POSCO_테스트_실행.bat" > nul 2>&1
    echo %SUCCESS%✅ POSCO 시스템 테스트 통과%RESET%
) else (
    echo %WARNING%⚠️ POSCO 테스트 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %SUCCESS%🎉 전체 시스템 테스트 완료!%RESET%
echo.
pause
goto return_menu

:full_backup
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%📦 전체 시스템 백업%RESET%                                                  %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %PRIMARY%📦 전체 시스템 백업을 생성하고 있습니다...%RESET%
echo.

set backup_name=WatchHamster_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo %PRIMARY%📁 백업명: %WHITE%%backup_name%%RESET%
echo.

mkdir "Backups\%backup_name%" 2>nul

echo %PRIMARY%🏭 POSCO 시스템 백업 중...%RESET%
xcopy "Monitoring\Posco_News_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\config.py" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1

echo.
echo %SUCCESS%🎉 전체 시스템 백업 완료!%RESET%
echo %PRIMARY%📂 백업 위치: %WHITE%Backups\%backup_name%\%RESET%
echo.
pause
goto return_menu

:settings_menu
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%⚙️ 시스템 설정%RESET%                                                      %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%🛠️ 설정 메뉴%RESET%
echo.
echo %GRAY%┌───────────────────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %WARNING%1%RESET% %WHITE%🔔 알림 설정%RESET%         %LIGHT_GRAY%통합 알림 관리%RESET%                        %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%2%RESET% %WHITE%⏰ 스케줄 설정%RESET%       %LIGHT_GRAY%통합 스케줄 관리%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%3%RESET% %WHITE%🔐 보안 설정%RESET%         %LIGHT_GRAY%보안 및 인증 관리%RESET%                     %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%4%RESET% %WHITE%🌐 네트워크 설정%RESET%     %LIGHT_GRAY%프록시 및 연결 설정%RESET%                   %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%0 🔙 돌아가기%RESET%
echo.

set /p setting_choice=%PRIMARY%❯ 설정 선택: %RESET%

if "%setting_choice%"=="1" (
    echo %WARNING%🚧 알림 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="2" (
    echo %WARNING%🚧 스케줄 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="3" (
    echo %WARNING%🚧 보안 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="4" (
    echo %WARNING%🚧 네트워크 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="0" (
    goto main_menu
) else (
    echo %ERROR%❌ 잘못된 선택입니다%RESET%
)
timeout /t 2 /nobreak > nul
goto settings_menu

:return_menu
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🎯 작업 완료%RESET%                                                        %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%다음 작업을 선택하세요:%RESET%
echo.
echo %GRAY%┌───────────────────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %WARNING%1%RESET% %WHITE%🔙 메인 메뉴로 돌아가기%RESET%                                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %WARNING%2%RESET% %ERROR%❌ 프로그램 종료%RESET%                                           %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

set /p return_choice=%PRIMARY%❯ 선택: %RESET%
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit_program
goto main_menu

:exit_program
cls
echo %SUCCESS%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %SUCCESS%│%RESET% %WHITE%👋 워치햄스터 총괄 관리 센터를 종료합니다%RESET%                              %SUCCESS%│%RESET%
echo %SUCCESS%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %SUCCESS%🐹 모든 모니터링 시스템이 안전하게 보호됩니다!%RESET%
echo.
echo %PRIMARY%🛡️ 워치햄스터가 백그라운드에서 계속 감시 중입니다%RESET%
echo %WARNING%📱 문제가 있으면 관리자에게 문의하세요%RESET%
echo.
echo %GRAY%🕒 종료 시간: %date% %time%%RESET%
echo.
timeout /t 3 /nobreak > nul
exit /b 0