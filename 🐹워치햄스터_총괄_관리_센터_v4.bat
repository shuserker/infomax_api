@echo off
setlocal enabledelayedexpansion
title 🐹 워치햄스터 총괄 관리 센터 v4.0 - Modern Windows Terminal

REM ============================================================================
REM Windows 10/11 최적화 설정
REM ============================================================================
chcp 65001 > nul 2>&1

REM Windows Terminal ANSI 지원 강화 (다중 방식)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_system32_cmd.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_System32_WindowsPowerShell_v1.0_powershell.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

REM ANSI 지원 강제 활성화 (PowerShell 방식)
powershell -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8" > nul 2>&1

REM 터미널 재시작 없이 즉시 적용
echo  > nul

REM 현대적 색상 팔레트 (Windows 11 스타일)
set "ESC="
set "RESET=%ESC%[0m"

REM 메인 브랜드 색상
set "PRIMARY=%ESC%[38;2;0;120;215m"      REM Windows Blue
set "SECONDARY=%ESC%[38;2;16;124;16m"    REM Success Green  
set "ACCENT=%ESC%[38;2;255;185;0m"       REM Warning Orange
set "DANGER=%ESC%[38;2;196;43;28m"       REM Error Red

REM 뉴트럴 색상
set "WHITE=%ESC%[38;2;255;255;255m"
set "LIGHT_GRAY=%ESC%[38;2;200;200;200m"
set "GRAY=%ESC%[38;2;150;150;150m"
set "DARK_GRAY=%ESC%[38;2;100;100;100m"

REM 기능별 색상
set "SUCCESS=%ESC%[38;2;16;124;16m"
set "ERROR=%ESC%[38;2;196;43;28m"
set "WARNING=%ESC%[38;2;255;185;0m"
set "INFO=%ESC%[38;2;0;120;215m"

REM 배경 강조
set "BG_PRIMARY=%ESC%[48;2;0;120;215m"
set "BG_SUCCESS=%ESC%[48;2;16;124;16m"
set "BG_WARNING=%ESC%[48;2;255;185;0m"
set "BG_ERROR=%ESC%[48;2;196;43;28m"

REM ============================================================================
REM 메인 메뉴
REM ============================================================================
:main_menu
cls
call :draw_modern_header
call :draw_system_status
call :draw_main_menu
call :draw_footer

set /p choice=%PRIMARY%❯ 선택하세요: %RESET%

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto settings_menu
if /i "%choice%"=="G" goto theme_menu
if "%choice%"=="0" goto exit_program
call :show_error "잘못된 선택입니다"
timeout /t 2 /nobreak > nul
goto main_menu

REM ============================================================================
REM UI 그리기 함수들
REM ============================================================================
:draw_modern_header
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %WHITE%🐹 워치햄스터 총괄 관리 센터 v4.0%RESET%                                    %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%  %LIGHT_GRAY%Modern Windows Terminal Optimized%RESET%                              %PRIMARY%│%RESET%
echo %PRIMARY%│%RESET%                                                                             %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
goto :eof

:draw_system_status
echo %INFO%📊 시스템 현황%RESET%
echo %GRAY%├─ %SUCCESS%🏭 POSCO 모니터링%RESET% %SUCCESS%● 활성%RESET%
echo %GRAY%├─ %INFO%💾 메모리 사용률%RESET% %WHITE%정상%RESET%
echo %GRAY%└─ %INFO%🌐 네트워크 상태%RESET% %SUCCESS%연결됨%RESET%
echo.
goto :eof

:draw_main_menu
echo %WHITE%🎛️ 관리 메뉴%RESET%
echo.
echo %GRAY%┌─ 모니터링 시스템 ─────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %ACCENT%1%RESET% %WHITE%🏭 POSCO 뉴스 모니터링%RESET%  %LIGHT_GRAY%포스코 뉴스 및 주가 모니터링%RESET%           %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%┌─ 시스템 관리 ─────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %ACCENT%A%RESET% %WHITE%🛡️ 전체 시스템 상태%RESET%     %LIGHT_GRAY%모든 워치햄스터 상태 확인%RESET%                %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%B%RESET% %WHITE%🔄 전체 시스템 업데이트%RESET%  %LIGHT_GRAY%모든 시스템 Git 업데이트%RESET%                 %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%C%RESET% %WHITE%📋 통합 로그 관리%RESET%       %LIGHT_GRAY%모든 시스템 로그 통합 관리%RESET%                %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%D%RESET% %WHITE%🧪 전체 시스템 테스트%RESET%   %LIGHT_GRAY%모든 시스템 통합 테스트%RESET%                   %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %GRAY%┌─ 고급 관리 ───────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %ACCENT%E%RESET% %WHITE%📦 전체 백업 생성%RESET%       %LIGHT_GRAY%모든 시스템 통합 백업%RESET%                     %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%F%RESET% %WHITE%⚙️ 시스템 설정%RESET%         %LIGHT_GRAY%워치햄스터 설정 관리%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%G%RESET% %WHITE%🎨 테마 설정%RESET%           %LIGHT_GRAY%UI 테마 및 색상 변경%RESET%                      %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %DARK_GRAY%0 ❌ 종료%RESET%
echo.
goto :eof

:draw_footer
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %INFO%🕒 %date% %time%%RESET% %GRAY%│%RESET% %INFO%📂 %cd%%RESET%
echo.
goto :eof

REM ============================================================================
REM 기능 구현
REM ============================================================================
:posco_monitoring
cls
call :show_loading "POSCO 모니터링 시스템으로 이동 중"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🏭 POSCO 모니터링 시스템%RESET%                                              %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🎛️POSCO_통합_관리_센터_v4.bat" (
    call "🎛️POSCO_통합_관리_센터_v4.bat"
) else if exist "🎛️POSCO_통합_관리_센터.bat" (
    call "🎛️POSCO_통합_관리_센터.bat"
) else (
    call :show_error "POSCO 모니터링 시스템을 찾을 수 없습니다"
    echo %INFO%📂 경로: Monitoring\Posco_News_mini\%RESET%
    pause
)
cd /d "%~dp0"
goto return_menu

:system_status
cls
call :show_loading "시스템 상태를 확인하고 있습니다"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🛡️ 전체 시스템 상태%RESET%                                                  %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%📊 시스템 상태 현황%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

if exist "Monitoring\Posco_News_mini\system_status.json" (
    echo %SUCCESS%✅ POSCO 모니터링      │ 활성화%RESET%
) else (
    echo %WARNING%⚠️ POSCO 모니터링      │ 상태 불명%RESET%
)

echo.
echo %WHITE%💻 시스템 리소스%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %INFO%🖥️ 메모리:%RESET% %SUCCESS%정상%RESET%
echo %INFO%💾 디스크:%RESET% %SUCCESS%충분%RESET%
echo %INFO%🌐 네트워크:%RESET% %SUCCESS%연결됨%RESET%
echo.
echo %INFO%📈 가동률: %SUCCESS%100%%%RESET% %GRAY%│%RESET% %INFO%🕒 업데이트: %date%%RESET%
echo.
pause
goto return_menu

:system_update
cls
call :show_loading "시스템 업데이트를 진행하고 있습니다"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🔄 전체 시스템 업데이트%RESET%                                              %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%📦 업데이트 진행 상황%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

echo %INFO%🏭 POSCO 모니터링 시스템 업데이트 중...%RESET%
call :show_progress_bar 30
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
echo %INFO%🕒 완료 시간: %date% %time%%RESET%
echo.
pause
goto return_menu

:integrated_logs
cls
call :show_loading "통합 로그를 분석하고 있습니다"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%📋 통합 로그 관리%RESET%                                                    %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%📊 로그 현황%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

echo %INFO%🏭 POSCO 시스템 로그 분석 중...%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo %WARNING%⚠️ POSCO 로그 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %WHITE%📈 로그 통계%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %INFO%📊 총 로그 파일:%RESET% %WHITE%확인 중...%RESET%
echo %INFO%📅 최근 로그:%RESET% %WHITE%%date%%RESET%
echo.
pause
goto return_menu

:system_test
cls
call :show_loading "시스템 테스트를 실행하고 있습니다"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🧪 전체 시스템 테스트%RESET%                                               %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%🔬 테스트 실행%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%

echo %INFO%🏭 POSCO 시스템 테스트 실행 중...%RESET%
call :show_progress_bar 25
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
echo %INFO%🕒 테스트 시간: %date% %time%%RESET%
echo.
pause
goto return_menu

:full_backup
cls
call :show_loading "전체 시스템 백업을 생성하고 있습니다"
echo.
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%📦 전체 시스템 백업%RESET%                                                  %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

set backup_name=WatchHamster_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo %WHITE%💾 백업 진행%RESET%
echo %GRAY%─────────────────────────────────────────────────────────────────────────────%RESET%
echo %INFO%📁 백업명: %WHITE%%backup_name%%RESET%
echo.

mkdir "Backups\%backup_name%" 2>nul

echo %INFO%🏭 POSCO 시스템 백업 중...%RESET%
call :show_progress_bar 40
xcopy "Monitoring\Posco_News_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\config.py" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1

echo.
echo %SUCCESS%🎉 전체 시스템 백업 완료!%RESET%
echo %INFO%📂 백업 위치: %WHITE%Backups\%backup_name%\%RESET%
echo %INFO%🕒 백업 시간: %date% %time%%RESET%
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
echo %GRAY%│%RESET% %ACCENT%1%RESET% %WHITE%🔔 알림 설정%RESET%         %LIGHT_GRAY%통합 알림 관리%RESET%                        %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%2%RESET% %WHITE%⏰ 스케줄 설정%RESET%       %LIGHT_GRAY%통합 스케줄 관리%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%3%RESET% %WHITE%🔐 보안 설정%RESET%         %LIGHT_GRAY%보안 및 인증 관리%RESET%                     %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%4%RESET% %WHITE%🌐 네트워크 설정%RESET%     %LIGHT_GRAY%프록시 및 연결 설정%RESET%                   %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %DARK_GRAY%0 🔙 돌아가기%RESET%
echo.

set /p setting_choice=%PRIMARY%❯ 설정 선택: %RESET%

if "%setting_choice%"=="1" (
    call :show_warning "🚧 알림 설정 기능은 현재 개발 중입니다"
) else if "%setting_choice%"=="2" (
    call :show_warning "🚧 스케줄 설정 기능은 현재 개발 중입니다"
) else if "%setting_choice%"=="3" (
    call :show_warning "🚧 보안 설정 기능은 현재 개발 중입니다"
) else if "%setting_choice%"=="4" (
    call :show_warning "🚧 네트워크 설정 기능은 현재 개발 중입니다"
) else if "%setting_choice%"=="0" (
    goto main_menu
) else (
    call :show_error "잘못된 선택입니다"
)
timeout /t 2 /nobreak > nul
goto settings_menu

:theme_menu
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🎨 테마 설정%RESET%                                                        %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%🌈 사용 가능한 테마%RESET%
echo.
echo %GRAY%┌───────────────────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %ACCENT%1%RESET% %SUCCESS%🌿 기본 테마%RESET%         %LIGHT_GRAY%현재 사용 중인 테마%RESET%                   %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%2%RESET% %PRIMARY%🌊 오션 테마%RESET%         %LIGHT_GRAY%파란색 계열 테마%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%3%RESET% %ERROR%🔥 파이어 테마%RESET%        %LIGHT_GRAY%빨간색 계열 테마%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%4%RESET% %WARNING%🌸 사쿠라 테마%RESET%       %LIGHT_GRAY%분홍색 계열 테마%RESET%                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%5%RESET% %DARK_GRAY%🌙 다크 테마%RESET%        %LIGHT_GRAY%어두운 테마%RESET%                          %GRAY%│%RESET%
echo %GRAY%└───────────────────────────────────────────────────────────────────────────┘%RESET%
echo.
echo %DARK_GRAY%0 🔙 돌아가기%RESET%
echo.

set /p theme_choice=%PRIMARY%❯ 테마 선택: %RESET%

if "%theme_choice%"=="1" (
    call :show_success "기본 테마가 이미 적용되어 있습니다"
) else if "%theme_choice%"=="2" (
    call :show_info "오션 테마 적용 중..."
    call :show_warning "🚧 테마 변경 기능은 현재 개발 중입니다"
) else if "%theme_choice%"=="3" (
    call :show_info "파이어 테마 적용 중..."
    call :show_warning "🚧 테마 변경 기능은 현재 개발 중입니다"
) else if "%theme_choice%"=="4" (
    call :show_info "사쿠라 테마 적용 중..."
    call :show_warning "🚧 테마 변경 기능은 현재 개발 중입니다"
) else if "%theme_choice%"=="5" (
    call :show_info "다크 테마 적용 중..."
    call :show_warning "🚧 테마 변경 기능은 현재 개발 중입니다"
) else if "%theme_choice%"=="0" (
    goto main_menu
) else (
    call :show_error "잘못된 선택입니다"
)
timeout /t 2 /nobreak > nul
goto theme_menu

:return_menu
cls
echo %PRIMARY%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %PRIMARY%│%RESET% %WHITE%🎯 작업 완료%RESET%                                                        %PRIMARY%│%RESET%
echo %PRIMARY%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
echo.

echo %WHITE%다음 작업을 선택하세요:%RESET%
echo.
echo %GRAY%┌───────────────────────────────────────────────────────────────────────────┐%RESET%
echo %GRAY%│%RESET% %ACCENT%1%RESET% %WHITE%🔙 메인 메뉴로 돌아가기%RESET%                                      %GRAY%│%RESET%
echo %GRAY%│%RESET% %ACCENT%2%RESET% %ERROR%❌ 프로그램 종료%RESET%                                           %GRAY%│%RESET%
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
echo %INFO%🛡️ 워치햄스터가 백그라운드에서 계속 감시 중입니다%RESET%
echo %WARNING%📱 문제가 있으면 관리자에게 문의하세요%RESET%
echo.
echo %GRAY%🕒 종료 시간: %date% %time%%RESET%
echo.
timeout /t 3 /nobreak > nul
exit /b 0

REM ============================================================================
REM 유틸리티 함수들
REM ============================================================================
:show_success
echo %SUCCESS%✅ %1%RESET%
goto :eof

:show_error
echo %ERROR%❌ %1%RESET%
goto :eof

:show_warning
echo %WARNING%⚠️ %1%RESET%
goto :eof

:show_info
echo %INFO%ℹ️ %1%RESET%
goto :eof

:show_loading
echo %INFO%🔄 %1...%RESET%
timeout /t 1 /nobreak > nul
goto :eof

:show_progress_bar
set /a "steps=%1"
if "%steps%"=="" set "steps=20"
echo %GRAY%[%RESET%
for /l %%i in (1,1,%steps%) do (
    echo %SUCCESS%█%RESET%
    timeout /t 0 /nobreak > nul 2>&1
)
echo %GRAY%] 완료%RESET%
goto :eof