@echo off
REM ============================================================================
REM Posco 테스트 실행
REM POSCO 시스템 테스트
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

setlocal enabledelayedexpansion
title 🧪 POSCO 알림 시스템 테스트

REM 공통 라이브러리 로드
call "lib_wt_common.ps1" init

cls
call :print_header "🧪 POSCO 알림 시스템 테스트 🛡️"

cd /d "%~dp0"

echo %CYAN%테스트할 알림 타입을 선택하세요:%RESET%
echo.
echo %YELLOW%1.%RESET% %GREEN%📊 영업일 비교 분석%RESET%
echo %YELLOW%2.%RESET% %ORANGE%⏰ 지연 발행 알림%RESET%
echo %YELLOW%3.%RESET% %BLUE%📊 일일 통합 분석 리포트%RESET%
echo %YELLOW%4.%RESET% %GREEN%✅ 정시 발행 알림%RESET%
echo %YELLOW%5.%RESET% %PURPLE%🔔 데이터 갱신 상태%RESET%
echo %YELLOW%6.%RESET% %CYAN%🎯 전체 테스트%RESET%
echo %YELLOW%0.%RESET% %RED%❌ 종료%RESET%
echo.

set /p test_choice=%GREEN%선택 (0-6): %RESET%

echo %CYAN%📅 테스트 날짜/시간 설정:%RESET%
set /p test_date=%GREEN%테스트 날짜 (YYYY-MM-DD, 엔터시 오늘): %RESET%
set /p test_time=%GREEN%테스트 시간 (HH:MM, 엔터시 현재시간): %RESET%

if "%test_choice%"=="1" (
    call :print_section "📊 영업일 비교 분석 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type business
    ) else (
        python posco_main_notifier.py --test --test-type business --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="2" (
    call :print_section "⏰ 지연 발행 알림 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type delay
    ) else (
        python posco_main_notifier.py --test --test-type delay --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="3" (
    call :print_section "📊 일일 통합 분석 리포트 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type report
    ) else (
        python posco_main_notifier.py --test --test-type report --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="4" (
    call :print_section "✅ 정시 발행 알림 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type timely
    ) else (
        python posco_main_notifier.py --test --test-type timely --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="5" (
    call :print_section "🔔 데이터 갱신 상태 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type status
    ) else (
        python posco_main_notifier.py --test --test-type status --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="6" (
    call :print_section "🎯 전체 테스트"
    if "%test_date%"=="" if "%test_time%"=="" (
        python posco_main_notifier.py --test --test-type all
    ) else (
        python posco_main_notifier.py --test --test-type all --test-date "%test_date%" --test-time "%test_time%"
    )
) else if "%test_choice%"=="0" (
    call :print_info "테스트를 종료합니다."
    exit /b 0
) else (
    call :print_error "잘못된 선택입니다."
    pause
    goto :eof
)

echo.
call :print_separator
echo %SUCCESS%✅ 테스트 완료!%RESET%
echo.

REM 재실행 옵션
echo %YELLOW%다음 중 선택하세요:%RESET%
echo %YELLOW%1.%RESET% %GREEN%🔄 다른 테스트 실행%RESET%
echo %YELLOW%2.%RESET% %CYAN%📋 로그 확인%RESET%
echo %YELLOW%3.%RESET% %RED%❌ 종료%RESET%
echo.

set /p restart_choice=%GREEN%선택 (1-3): %RESET%

if "%restart_choice%"=="1" (
    goto :eof
) else if "%restart_choice%"=="2" (
    if exist ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/main_notifier.log" (
        call :print_section "📄 최근 로그"
        type ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/main_notifier.log" | tail -20 2>nul || (
            powershell "Get-Content '.naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/main_notifier.log' | Select-Object -Last 20"
        )
    ) else (
        call :print_info "로그 파일이 없습니다."
    )
    pause
) else (
    call :print_info "테스트를 종료합니다."
)

exit /b 0