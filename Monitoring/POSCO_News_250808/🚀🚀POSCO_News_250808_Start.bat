@echo off
REM ============================================================================
REM POSCO News 250808 Start
REM POSCO 시스템 구성요소
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

setlocal enabledelayedexpansion
title 🎛️ POSCO WatchHamster v3.0 Control Panel

REM 공통 라이브러리 로드
call "lib_wt_common.ps1" init

cls
call :print_header "🐹 POSCO WatchHamster v3.0 시작 🛡️"

call :print_section "📋 시스템 초기화"

cd /d "%~dp0"

REM Python 환경 확인
call :show_loading "Python 환경 확인 중"
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python이 설치되지 않았거나 PATH에 없습니다."
    call :print_info "📥 Python 3.8 이상을 설치해주세요."
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do (
        call :print_success "Python %%v 확인됨"
    )
)

REM 필수 모듈 확인
call :show_loading "필수 모듈 확인 중"
# BROKEN_REF: python -c "import requests, schedule, datetime" >nul 2>&1
if errorlevel 1 (
    call :print_warning "일부 필수 모듈이 없습니다. 설치를 시도합니다..."
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            call :print_error "모듈 설치에 실패했습니다."
            pause
            exit /b 1
        ) else (
            call :print_success "필수 모듈 설치 완료"
        )
    ) else (
        call :print_error "requirements.txt 파일을 찾을 수 없습니다."
        pause
        exit /b 1
    )
) else (
    call :print_success "필수 모듈 확인 완료"
)

REM 설정 파일 확인
if exist "config.py" (
    call :print_success "설정 파일 확인됨"
) else (
    call :print_warning "config.py 파일을 찾을 수 없습니다."
    call :print_info "기본 설정으로 실행됩니다."
)

REM 메인 알림 시스템 파일 확인
if exist "posco_main_notifier.py" (
    call :print_success "메인 알림 시스템 파일 확인됨"
) else (
    call :print_error "posco_main_notifier.py 파일을 찾을 수 없습니다."
    pause
    exit /b 1
)

echo.
call :print_section "🚀 워치햄스터 시작"
echo %SUCCESS%🐹 POSCO WatchHamster v3.0 시작합니다...%RESET%
echo %INFO%💡 중단하려면 Ctrl+C를 누르거나 창을 닫으세요.%RESET%
echo %INFO%🔄 24시간 모니터링이 시작됩니다.%RESET%
echo.

call :print_separator
echo %CYAN%📊 모니터링 대상:%RESET%
echo %WHITE%  • POSCO 뉴스 모니터링%RESET%
echo %WHITE%  • 주가 정보 수집%RESET%
echo %WHITE%  • 실시간 알림 시스템%RESET%
echo %WHITE%  • 자동 리포트 생성%RESET%
call :print_separator
echo.

REM 시작 시간 기록
echo %INFO%🕒 시작 시간: %date% %time%%RESET%
echo.

REM 메인 알림 시스템 실행
python posco_main_notifier.py

REM 종료 처리
echo.
call :print_separator
echo %WARNING%⚠️ 메인 알림 시스템이 종료되었습니다.%RESET%
echo %INFO%🕒 종료 시간: %date% %time%%RESET%
echo.

REM 재시작 옵션
echo %YELLOW%다음 중 선택하세요:%RESET%
echo %YELLOW%1.%RESET% %GREEN%🔄 메인 알림 시스템 재시작%RESET%
echo %YELLOW%2.%RESET% %CYAN%📋 로그 확인%RESET%
echo %YELLOW%3.%RESET% %RED%❌ 종료%RESET%
echo.

set /p restart_choice=%GREEN%선택 (1-3): %RESET%

if "%restart_choice%"=="1" (
    call :print_info "메인 알림 시스템을 재시작합니다..."
    timeout /t 3 /nobreak >nul
    goto restart_hamster
) else if "%restart_choice%"=="2" (
    if exist "*.log" (
        call :print_section "📄 최근 로그"
        for %%f in (*.log) do (
            echo %CYAN%📄 %%f (최근 10줄):%RESET%
            type "%%f" | tail -10 2>nul || (
                for /f "skip=0 tokens=*" %%a in ('type "%%f"') do (
                    set /a count+=1
                    if !count! gtr 10 set "line=%%a"
                )
                echo !line!
            )
            echo.
        )
    ) else (
        call :print_info "로그 파일이 없습니다."
    )
    pause
) else (
    call :print_info "메인 알림 시스템을 종료합니다."
)

exit /b 0

:restart_hamster
cls
call :print_header "🔄 POSCO WatchHamster v3.0 시작"
call :show_loading "시스템을 재시작하고 있습니다"
goto start_monitoring

:start_monitoring
echo %SUCCESS%🐹 POSCO WatchHamster v3.0 시작합니다...%RESET%
echo %INFO%💡 중단하려면 Ctrl+C를 누르거나 창을 닫으세요.%RESET%
echo.
python posco_main_notifier.py
goto restart_option