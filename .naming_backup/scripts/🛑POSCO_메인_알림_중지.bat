@echo off
setlocal enabledelayedexpansion
title 🛑 POSCO 모니터링 중지 v3.0 - Windows Terminal 최적화

REM 공통 라이브러리 로드
call "lib_wt_common.ps1" init

cls
call :print_header "🛑 POSCO 모니터링 시스템 중지"

call :print_section "🔍 실행 중인 프로세스 확인"

REM Python 프로세스 확인
call :show_loading "워치햄스터 프로세스를 검색하고 있습니다"

tasklist /fi "imagename eq python.exe" | find "python.exe" >nul
if not errorlevel 1 (
    call :print_warning "실행 중인 Python 프로세스를 발견했습니다."
    echo.
    
    call :print_section "📊 실행 중인 프로세스 목록"
    echo %CYAN%다음 프로세스들이 실행 중입니다:%RESET%
    echo.
    
    REM 프로세스 정보를 표 형태로 출력
    echo %HEADER%PID      프로세스명           메모리 사용량    실행 시간%RESET%
    call :print_separator
    
    for /f "tokens=1,2,4,5" %%a in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /v "Image"') do (
        set "pid=%%a"
        set "name=%%b"
        set "memory=%%c"
        set "time=%%d"
        
        REM 따옴표 제거
        set "pid=!pid:"=!"
        set "name=!name:"=!"
        set "memory=!memory:"=!"
        set "time=!time:"=!"
        
        echo %WHITE%!pid!      !name!           !memory!    !time!%RESET%
    )
    
    echo.
    call :print_separator
    
    REM 사용자 확인
    echo %RED%⚠️ 경고: 모든 Python 프로세스가 종료됩니다!%RESET%
    echo %YELLOW%이 작업은 실행 중인 모든 Python 스크립트를 중지시킵니다.%RESET%
    echo.
    
    set /p confirm=%RED%정말로 모든 Python 프로세스를 종료하시겠습니까? (Y/N): %RESET%
    
    if /i "!confirm!"=="Y" (
        call :print_section "🛑 프로세스 종료 중"
        call :show_loading "워치햄스터 프로세스를 종료하고 있습니다"
        
        REM 프로세스 강제 종료
        taskkill /f /im python.exe >nul 2>&1
        
        REM 종료 확인
        timeout /t 2 /nobreak >nul
        tasklist /fi "imagename eq python.exe" | find "python.exe" >nul
        if errorlevel 1 (
            call :print_success "모든 워치햄스터 프로세스가 성공적으로 종료되었습니다."
            
            REM 종료 통계
            echo.
            call :print_section "📊 종료 통계"
            echo %INFO%🕒 종료 시간: %date% %time%%RESET%
            echo %INFO%🔄 종료된 프로세스: Python 워치햄스터%RESET%
            echo %INFO%💾 메모리 해제: 완료%RESET%
            
        ) else (
            call :print_warning "일부 프로세스가 여전히 실행 중일 수 있습니다."
            call :print_info "시스템을 재부팅하거나 작업 관리자를 사용하여 수동으로 종료하세요."
        )
        
    ) else (
        call :print_info "작업이 취소되었습니다."
        call :print_success "워치햄스터는 계속 실행됩니다."
    )
    
) else (
    call :print_info "실행 중인 워치햄스터 프로세스가 없습니다."
    
    call :print_section "🔍 추가 확인"
    
    REM 포트 사용 확인
    netstat -an | find ":8000" >nul
    if not errorlevel 1 (
        call :print_warning "포트 8000이 사용 중입니다. 다른 서비스가 실행 중일 수 있습니다."
    ) else (
        call :print_success "관련 포트가 모두 해제되어 있습니다."
    )
    
    REM 로그 파일 확인
# BROKEN_REF:     if exist "*.log" (
        call :print_info "로그 파일이 존재합니다. 최근 활동을 확인할 수 있습니다."
        
        echo %YELLOW%최근 로그를 확인하시겠습니까? (Y/N): %RESET%
        set /p log_check=
        
        if /i "!log_check!"=="Y" (
            call :print_section "📄 최근 로그 (마지막 10줄)"
            for %%f in (*.log) do (
                echo %CYAN%📄 %%f:%RESET%
                type "%%f" | tail -10 2>nul || (
                    REM tail 명령어가 없는 경우 대체 방법
                    for /f "tokens=*" %%a in ('type "%%f"') do set "lastline=%%a"
                    echo !lastline!
                )
                echo.
            )
        )
    ) else (
        call :print_success "로그 파일도 없습니다. 시스템이 완전히 정리되어 있습니다."
    )
)

echo.
call :print_section "🎯 다음 단계"
echo %YELLOW%다음 중 원하는 작업을 선택하세요:%RESET%
echo.
echo %YELLOW%1.%RESET% %GREEN%🚀 워치햄스터 다시 시작%RESET%
echo %YELLOW%2.%RESET% %CYAN%📊 시스템 상태 확인%RESET%
echo %YELLOW%3.%RESET% %BLUE%📋 로그 전체 보기%RESET%
echo %YELLOW%4.%RESET% %MAGENTA%🔧 관리 센터로 이동%RESET%
echo %YELLOW%5.%RESET% %RED%❌ 종료%RESET%
echo.

set /p next_action=%GREEN%선택 (1-5): %RESET%

if "%next_action%"=="1" (
    call :print_info "워치햄스터를 다시 시작합니다..."
    if exist ".naming_backup/config_data_backup/watchhamster.log" (
        call ".naming_backup/config_data_backup/watchhamster.log"
    ) else if exist ".naming_backup/config_data_backup/watchhamster.log" (
        call ".naming_backup/config_data_backup/watchhamster.log"
    ) else (
        call :print_error "워치햄스터 시작 스크립트를 찾을 수 없습니다."
    )
    
) else if "%next_action%"=="2" (
    call :print_section "💻 시스템 상태"
    
    REM CPU 사용률
    echo %INFO%🖥️ CPU 사용률:%RESET%
    wmic cpu get loadpercentage /value | findstr "LoadPercentage" 2>nul
    
    REM 메모리 사용률
    echo %INFO%💾 메모리 상태:%RESET%
    wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list | findstr "=" 2>nul
    
    REM 디스크 공간
    echo %INFO%💿 디스크 공간:%RESET%
    for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do echo %WHITE%사용 가능: %%a bytes%RESET%
    
    pause
    
) else if "%next_action%"=="3" (
# BROKEN_REF:     if exist "*.log" (
        call :print_section "📚 전체 로그 파일"
        for %%f in (*.log) do (
            echo.
            echo %HEADER%📄 %%f 전체 내용:%RESET%
            call :print_separator
            type "%%f"
            call :print_separator
            echo.
            pause
        )
    ) else (
        call :print_info "표시할 로그 파일이 없습니다."
        pause
    )
    
) else if "%next_action%"=="4" (
    call :print_info "관리 센터로 이동합니다..."
# BROKEN_REF:     if exist "🎛️POSCO_통합_관리_센터_v3.bat" (
# BROKEN_REF:         call "🎛️POSCO_통합_관리_센터_v3.bat"
# BROKEN_REF:     ) else if exist "🎛️POSCO_통합_관리_센터.bat" (
# BROKEN_REF:         call "🎛️POSCO_통합_관리_센터.bat"
    ) else (
        call :print_error "관리 센터 스크립트를 찾을 수 없습니다."
        pause
    )
    
) else (
    call :print_info "프로그램을 종료합니다."
)

echo.
call :print_section "👋 종료"
echo %SUCCESS%🛑 POSCO 모니터링 중지 작업이 완료되었습니다.%RESET%
echo %INFO%🕒 작업 완료 시간: %date% %time%%RESET%
echo.

pause
exit /b 0