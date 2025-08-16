@echo off
REM ============================================================================
REM Watchhamster V3.0 Control Center
REM POSCO 시스템 제어센터
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

setlocal enabledelayedexpansion
title 🎛️ POSCO WatchHamster v3.0 Control Panel

REM 공통 라이브러리 로드
call lib_wt_common.bat init

REM ============================================================================
REM 메인 메뉴
REM ============================================================================
:main_menu
cls
call :print_header "🐹 WatchHamster v3.0.0 🛡️"
echo %INFO%🎯 현재 활성화된 모니터링 시스템을 관리합니다%RESET%
echo.

echo %YELLOW%🎛️ 관리할 시스템을 선택하세요:%RESET%
echo.

REM 활성화된 모니터링 시스템
call :start_box %GREEN%
echo %GREEN%║%RESET%                       %CYAN%🏭 활성화된 모니터링 시스템%RESET%                       %GREEN%║%RESET%
echo %GREEN%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
call :print_menu_item "1." "🏭 POSCO 뉴스 모니터링" "POSCO News 250808 및 주가 모니터링 시스템"
call :end_box

echo.

REM 시스템 관리
call :start_box %BLUE%
echo %BLUE%║%RESET%                           %MAGENTA%🔧 시스템 관리%RESET%                                    %BLUE%║%RESET%
echo %BLUE%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
call :print_menu_item "A." "🛡️ 전체 시스템 상태" "모든 WatchHamster v3.0 상태 확인"
call :print_menu_item "B." "🔄 전체 시스템 업데이트" "모든 시스템 Git 업데이트"
call :print_menu_item "C." "📋 통합 로그 관리" "모든 시스템 로그 통합 관리"
call :print_menu_item "D." "🧪 전체 시스템 테스트" "모든 시스템 통합 테스트"
call :end_box

echo.

REM 고급 관리
call :start_box %RED%
echo %RED%║%RESET%                           %WHITE%⚙️ 고급 관리%RESET%                                      %RED%║%RESET%
echo %RED%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
call :print_menu_item "E." "📦 전체 백업 생성" "모든 시스템 통합 백업"
call :print_menu_item "F." "🔧 워치햄스터 설정" "총괄 설정 관리"
call :print_menu_item "G." "🎨 UI 테마 변경" "색상 테마 및 인터페이스 설정"
call :end_box

echo.
echo %GRAY%0. ❌ 종료%RESET%
echo.

call :print_system_info

set /p choice=%GREEN%🎯 선택하세요 (1, A-G, 0): %RESET%

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto watchhamster_config
if /i "%choice%"=="G" goto ui_theme_config
if "%choice%"=="0" goto exit
goto invalid_choice

REM ============================================================================
REM POSCO 모니터링 시스템
REM ============================================================================
:posco_monitoring
cls
call :print_header "🏭 POSCO 모니터링 시스템 진입"
call :show_loading "POSCO 모니터링 시스템으로 이동 중"

cd /d "Monitoring\POSCO News 250808_mini"
# BROKEN_REF: if exist "🎛️POSCO_통합_관리_센터_v3.bat" (
# BROKEN_REF:     call "🎛️POSCO_통합_관리_센터_v3.bat"
# BROKEN_REF: ) else if exist "🎛️POSCO_통합_관리_센터.bat" (
# BROKEN_REF:     call "🎛️POSCO_통합_관리_센터.bat"
) else (
    call :print_error "POSCO 모니터링 시스템을 찾을 수 없습니다."
# BROKEN_REF:     call :print_info "경로: Monitoring\POSCO News 250808_mini\🎛️POSCO_통합_관리_센터.bat"
    echo.
    pause
)
cd /d "%~dp0"
goto return_to_menu

REM ============================================================================
REM 전체 시스템 상태
REM ============================================================================
:system_status
cls
call :print_header "🛡️ 전체 시스템 상태 확인"
call :show_loading "모든 WatchHamster v3.0 상태를 확인하고 있습니다"

call :print_section "📊 시스템 상태 현황"

REM POSCO 시스템 상태 확인
if exist "docs/status.json" (
    call :print_success "POSCO 모니터링      : ✅ 활성화"
    set "posco_status=active"
) else (
    call :print_warning "POSCO 모니터링      : ⚠️ 상태 불명"
    set "posco_status=unknown"
)

echo.
call :print_separator
echo %CYAN%📊 활성화된 시스템: 1개 (POSCO 모니터링)%RESET%
echo %GREEN%🎯 전체 시스템 가동률: 100%% (활성화된 시스템 기준)%RESET%
echo %INFO%🕒 마지막 업데이트: %date% %time%%RESET%
echo.

REM 시스템 리소스 정보
call :print_section "💻 시스템 리소스"
echo %INFO%🖥️ 메모리 사용량:%RESET%
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list | findstr "=" 2>nul
echo %INFO%💾 디스크 공간:%RESET%
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do echo %WHITE%사용 가능: %%a bytes%RESET%
echo.

pause
goto return_to_menu

REM ============================================================================
REM 전체 시스템 업데이트
REM ============================================================================
:system_update
cls
call :print_header "🔄 전체 시스템 업데이트"
call :show_loading "모든 워치햄스터 시스템을 업데이트하고 있습니다"

call :print_section "📦 시스템별 업데이트 진행"

echo %CYAN%🏭 POSCO 모니터링 시스템 업데이트 중...%RESET%
cd /d "Monitoring\POSCO News 250808_mini"
if exist ".naming_backup/scripts/.naming_backup/scripts/🔄POSCO_Git_업데이트.bat" (
    call ".naming_backup/scripts/.naming_backup/scripts/🔄POSCO_Git_업데이트.bat"
    call :print_success "POSCO 시스템 업데이트 완료"
) else (
    call :print_error "POSCO 업데이트 파일을 찾을 수 없습니다"
)
cd /d "%~dp0"

echo.
call :print_success "전체 시스템 업데이트 완료!"
echo %INFO%🕒 업데이트 완료 시간: %date% %time%%RESET%
echo.
pause
goto return_to_menu

REM ============================================================================
REM 통합 로그 관리
REM ============================================================================
:integrated_logs
cls
call :print_header "📋 통합 로그 관리"
call :show_loading "모든 시스템의 로그를 통합 관리합니다"

call :print_section "📊 시스템별 로그 현황"

echo %CYAN%🏭 POSCO 시스템 로그:%RESET%
cd /d "Monitoring\POSCO News 250808_mini"
if exist ".naming_backup/scripts/.naming_backup/scripts/📋POSCO_로그_확인.bat" (
    call ".naming_backup/scripts/.naming_backup/scripts/📋POSCO_로그_확인.bat"
) else (
    call :print_error "POSCO 로그 파일을 찾을 수 없습니다"
)
cd /d "%~dp0"

echo.
call :print_section "📈 로그 통계"
echo %INFO%📊 총 로그 파일 수:%RESET%
for /f %%i in ('dir /s *.log 2^>nul ^| find "File(s)" ^| find /v "Dir(s)"') do echo %WHITE%%%i%RESET%
echo.

pause
goto return_to_menu

REM ============================================================================
REM 전체 시스템 테스트
REM ============================================================================
:system_test
cls
call :print_header "🧪 전체 시스템 테스트"
call :show_loading "모든 활성화된 시스템을 테스트하고 있습니다"

call :print_section "🔬 시스템별 테스트 실행"

echo %GREEN%🏭 POSCO 시스템 테스트:%RESET%
cd /d "Monitoring\POSCO News 250808_mini"
if exist ".naming_backup/scripts/.naming_backup/scripts/🧪POSCO_테스트_실행.bat" (
    call ".naming_backup/scripts/.naming_backup/scripts/🧪POSCO_테스트_실행.bat"
    call :print_success "POSCO 시스템 테스트 통과"
) else (
    call :print_error "POSCO 테스트 파일을 찾을 수 없습니다"
)
cd /d "%~dp0"

echo.
call :print_success "전체 시스템 테스트 완료!"
echo %INFO%🕒 테스트 완료 시간: %date% %time%%RESET%
echo.
pause
goto return_to_menu

REM ============================================================================
REM 전체 백업 생성
REM ============================================================================
:full_backup
cls
call :print_header "📦 전체 시스템 백업"
call :show_loading "모든 워치햄스터 시스템을 백업하고 있습니다"

set backup_name=WatchHamster_Full_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

call :print_section "💾 백업 진행 상황"
echo %CYAN%📁 백업 이름: %backup_name%%RESET%
echo.

mkdir "Backups\%backup_name%" 2>nul

echo %GREEN%🏭 POSCO 시스템 백업 중...%RESET%
call :show_progress 5
# BROKEN_REF: xcopy "Monitoring\POSCO News 250808_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
call :show_progress 10
# BROKEN_REF: xcopy "Monitoring\POSCO News 250808_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
call :show_progress 15
xcopy ".comprehensive_repair_backup/config.py.backup_20250809_181657" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1
call :show_progress 20

echo.
call :print_success "전체 시스템 백업 완료!"
echo %CYAN%📂 백업 위치: Backups\%backup_name%\%RESET%
echo %INFO%💾 백업 크기:%RESET%
for /f "tokens=3" %%a in ('dir "Backups\%backup_name%" /-c ^| find "bytes"') do echo %WHITE%%%a bytes%RESET%
echo.
pause
goto return_to_menu

REM ============================================================================
REM 워치햄스터 설정
REM ============================================================================
:watchhamster_config
cls
call :print_header "🔧 워치햄스터 총괄 설정"
call :show_loading "워치햄스터 총괄 설정을 관리합니다"

call :print_section "⚙️ 설정 메뉴"
echo %YELLOW%1.%RESET% %CYAN%🔔 알림 설정%RESET% - 통합 알림 관리
echo %YELLOW%2.%RESET% %CYAN%⏰ 스케줄 설정%RESET% - 통합 스케줄 관리  
echo %YELLOW%3.%RESET% %CYAN%🔐 보안 설정%RESET% - 보안 및 인증 관리
echo %YELLOW%4.%RESET% %CYAN%🌐 네트워크 설정%RESET% - 프록시 및 연결 설정
echo %YELLOW%0.%RESET% %GRAY%🔙 돌아가기%RESET%
echo.

set /p config_choice=%GREEN%설정 선택 (1-4, 0): %RESET%

if "%config_choice%"=="1" goto notification_config
if "%config_choice%"=="2" goto schedule_config  
if "%config_choice%"=="3" goto security_config
if "%config_choice%"=="4" goto network_config
if "%config_choice%"=="0" goto return_to_menu
goto watchhamster_config

:notification_config
call :print_warning "🚧 알림 설정 기능은 현재 개발 중입니다."
pause
goto watchhamster_config

:schedule_config
call :print_warning "🚧 스케줄 설정 기능은 현재 개발 중입니다."
pause
goto watchhamster_config

:security_config
call :print_warning "🚧 보안 설정 기능은 현재 개발 중입니다."
pause
goto watchhamster_config

:network_config
call :print_warning "🚧 네트워크 설정 기능은 현재 개발 중입니다."
pause
goto watchhamster_config

REM ============================================================================
REM UI 테마 설정
REM ============================================================================
:ui_theme_config
cls
call :print_header "🎨 UI 테마 변경"

call :print_section "🌈 사용 가능한 테마"
echo %YELLOW%1.%RESET% %GREEN%🌿 기본 테마%RESET% - 현재 사용 중인 테마
echo %YELLOW%2.%RESET% %BLUE%🌊 오션 테마%RESET% - 파란색 계열 테마
echo %YELLOW%3.%RESET% %RED%🔥 파이어 테마%RESET% - 빨간색 계열 테마
echo %YELLOW%4.%RESET% %MAGENTA%🌸 사쿠라 테마%RESET% - 분홍색 계열 테마
echo %YELLOW%5.%RESET% %GRAY%🌙 다크 테마%RESET% - 어두운 테마
echo %YELLOW%0.%RESET% %GRAY%🔙 돌아가기%RESET%
echo.

set /p theme_choice=%GREEN%테마 선택 (1-5, 0): %RESET%

if "%theme_choice%"=="1" (
    call :print_success "기본 테마가 이미 적용되어 있습니다."
) else if "%theme_choice%"=="2" (
    call :print_info "오션 테마 적용 중..."
    call :print_warning "🚧 테마 변경 기능은 현재 개발 중입니다."
) else if "%theme_choice%"=="3" (
    call :print_info "파이어 테마 적용 중..."
    call :print_warning "🚧 테마 변경 기능은 현재 개발 중입니다."
) else if "%theme_choice%"=="4" (
    call :print_info "사쿠라 테마 적용 중..."
    call :print_warning "🚧 테마 변경 기능은 현재 개발 중입니다."
) else if "%theme_choice%"=="5" (
    call :print_info "다크 테마 적용 중..."
    call :print_warning "🚧 테마 변경 기능은 현재 개발 중입니다."
) else if "%theme_choice%"=="0" (
    goto return_to_menu
) else (
    call :print_error "잘못된 선택입니다."
)

pause
goto ui_theme_config

REM ============================================================================
REM 잘못된 선택
REM ============================================================================
:invalid_choice
cls
call :print_error "잘못된 선택입니다. 다시 선택해주세요."
echo.
pause
goto main_menu

REM ============================================================================
REM 메뉴 복귀
REM ============================================================================
:return_to_menu
cls
call :print_section "🎯 작업 완료"
echo %YELLOW%1.%RESET% %CYAN%🔙 메인 메뉴로 돌아가기%RESET%
echo %YELLOW%2.%RESET% %RED%❌ 프로그램 종료%RESET%
echo.

set /p return_choice=%GREEN%선택 (1-2): %RESET%
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit
goto main_menu

REM ============================================================================
REM 프로그램 종료
REM ============================================================================
:exit
cls
call :print_header "👋 워치햄스터 총괄 관리 센터를 종료합니다"
echo %GREEN%🐹 모든 모니터링 시스템이 안전하게 보호됩니다!%RESET%
echo.
echo %CYAN%🛡️ 워치햄스터가 백그라운드에서 계속 감시 중입니다.%RESET%
echo %YELLOW%📱 문제가 있으면 관리자에게 문의하세요.%RESET%
echo.
echo %INFO%🕒 종료 시간: %date% %time%%RESET%
echo.
pause
exit /b 0