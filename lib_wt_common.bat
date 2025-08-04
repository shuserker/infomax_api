@echo off
REM ============================================================================
REM Windows Terminal 최적화 공통 라이브러리 v4.0
REM Windows 10/11 Modern Terminal 최적화
REM 모든 워치햄스터 배치 파일에서 사용하는 공통 함수들
REM ============================================================================

REM UTF-8 인코딩 설정 (Windows 10/11 최적화)
chcp 65001 > nul 2>&1

REM Windows Terminal ANSI 지원 강화 (레지스트리 기반)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_system32_cmd.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
reg add "HKCU\Console\%%SystemRoot%%_system32_WindowsPowerShell_v1.0_powershell.exe" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

REM ============================================================================
REM 현대적 색상 팔레트 (Windows 11 Fluent Design 기반)
REM ============================================================================
set "ESC="

REM 기본 제어
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"
set "DIM=%ESC%[2m"
set "UNDERLINE=%ESC%[4m"

REM Windows 11 Fluent Design 색상 (RGB 기반)
set "PRIMARY=%ESC%[38;2;0;120;215m"      REM Windows Blue
set "SECONDARY=%ESC%[38;2;16;124;16m"    REM Success Green  
set "ACCENT=%ESC%[38;2;255;185;0m"       REM Warning Orange
set "DANGER=%ESC%[38;2;196;43;28m"       REM Error Red

REM 뉴트럴 색상 (고대비 지원)
set "WHITE=%ESC%[38;2;255;255;255m"
set "LIGHT_GRAY=%ESC%[38;2;200;200;200m"
set "GRAY=%ESC%[38;2;150;150;150m"
set "DARK_GRAY=%ESC%[38;2;100;100;100m"
set "BLACK=%ESC%[38;2;0;0;0m"

REM 기능별 색상 (접근성 고려)
set "SUCCESS=%ESC%[38;2;16;124;16m"
set "ERROR=%ESC%[38;2;196;43;28m"
set "WARNING=%ESC%[38;2;255;185;0m"
set "INFO=%ESC%[38;2;0;120;215m"

REM 배경 강조 (선택적 사용)
set "BG_PRIMARY=%ESC%[48;2;0;120;215m"
set "BG_SUCCESS=%ESC%[48;2;16;124;16m"
set "BG_WARNING=%ESC%[48;2;255;185;0m"
set "BG_ERROR=%ESC%[48;2;196;43;28m"

REM 레거시 호환성 (기존 코드 지원)
set "RED=%ERROR%"
set "GREEN=%SUCCESS%"
set "YELLOW=%WARNING%"
set "BLUE=%INFO%"
set "CYAN=%INFO%"
set "MAGENTA=%ACCENT%"
set "HEADER=%PRIMARY%%BOLD%"

REM ============================================================================
REM 공통 함수들
REM ============================================================================

REM 함수: 헤더 출력
:print_header
echo %HEADER%████████████████████████████████████████████████████████████████████████████████%RESET%
echo %HEADER%██                                                                            ██%RESET%
echo %HEADER%██    %1                                         ██%RESET%
echo %HEADER%██                                                                            ██%RESET%
echo %HEADER%████████████████████████████████████████████████████████████████████████████████%RESET%
echo.
goto :eof

REM 함수: 섹션 헤더 출력
:print_section
echo %CYAN%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║%RESET%                           %1                                    %CYAN%║%RESET%
echo %CYAN%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.
goto :eof

REM 함수: 성공 메시지
:print_success
echo %SUCCESS%✅ %1%RESET%
goto :eof

REM 함수: 에러 메시지
:print_error
echo %ERROR%❌ %1%RESET%
goto :eof

REM 함수: 경고 메시지
:print_warning
echo %WARNING%⚠️ %1%RESET%
goto :eof

REM 함수: 정보 메시지
:print_info
echo %INFO%ℹ️ %1%RESET%
goto :eof

REM 함수: 로딩 애니메이션
:show_loading
echo %YELLOW%🔄 %1...%RESET%
timeout /t 1 /nobreak > nul
goto :eof

REM 함수: 구분선
:print_separator
echo %GRAY%────────────────────────────────────────────────────────────────────────────────%RESET%
goto :eof

REM 함수: 시스템 정보 출력
:print_system_info
echo %INFO%📍 현재 시간:%RESET% %WHITE%%date% %time%%RESET%
echo %INFO%🖥️ 시스템:%RESET% %WHITE%Windows Terminal 최적화%RESET%
echo %INFO%📂 작업 디렉토리:%RESET% %WHITE%%cd%%RESET%
echo.
goto :eof

REM 함수: 메뉴 아이템 출력
:print_menu_item
echo %GREEN%║%RESET%  %YELLOW%%1%RESET% %CYAN%%2%RESET% - %3          %GREEN%║%RESET%
goto :eof

REM 함수: 박스 시작
:start_box
set "box_color=%1"
if "%box_color%"=="" set "box_color=%GREEN%"
echo %box_color%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
goto :eof

REM 함수: 박스 끝
:end_box
if "%box_color%"=="" set "box_color=%GREEN%"
echo %box_color%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
goto :eof

REM 함수: 진행률 표시
:show_progress
set /a "progress=%1"
set "bar="
for /l %%i in (1,1,%progress%) do set "bar=!bar!█"
for /l %%i in (%progress%,1,20) do set "bar=!bar!░"
echo %CYAN%[%bar%] %progress%/20%RESET%
goto :eof

REM 함수: 현대적 카드 스타일 박스
:draw_card
set "card_title=%1"
set "card_color=%2"
if "%card_color%"=="" set "card_color=%PRIMARY%"
echo %card_color%┌─────────────────────────────────────────────────────────────────────────────┐%RESET%
echo %card_color%│%RESET% %WHITE%%card_title%%RESET%                                                        %card_color%│%RESET%
echo %card_color%└─────────────────────────────────────────────────────────────────────────────┘%RESET%
goto :eof

REM 함수: 현대적 리스트 아이템
:draw_list_item
set "item_key=%1"
set "item_title=%2"
set "item_desc=%3"
echo %GRAY%│%RESET% %ACCENT%%item_key%%RESET% %WHITE%%item_title%%RESET% %LIGHT_GRAY%%item_desc%%RESET%           %GRAY%│%RESET%
goto :eof

REM 함수: 상태 표시기
:show_status
set "status_text=%1"
set "status_type=%2"
if "%status_type%"=="success" echo %SUCCESS%● %status_text%%RESET%
if "%status_type%"=="error" echo %ERROR%● %status_text%%RESET%
if "%status_type%"=="warning" echo %WARNING%● %status_text%%RESET%
if "%status_type%"=="info" echo %INFO%● %status_text%%RESET%
goto :eof

REM 함수: 현대적 진행률 표시
:show_modern_progress
set /a "progress=%1"
set "progress_text=%2"
if "%progress_text%"=="" set "progress_text=진행 중"
set "bar="
set /a "filled=%progress%/5"
set /a "empty=20-%filled%"
for /l %%i in (1,1,%filled%) do set "bar=!bar!█"
for /l %%i in (1,1,%empty%) do set "bar=!bar!░"
echo %INFO%[%SUCCESS%%bar%%INFO%] %progress%%%% %progress_text%%RESET%
goto :eof

REM ============================================================================
REM 초기화 완료 메시지
REM ============================================================================
if "%1"=="init" (
    echo %SUCCESS%✅ Windows Terminal 공통 라이브러리 v4.0 로드 완료%RESET%
    echo %INFO%🎨 Modern Windows 11 Fluent Design 적용%RESET%
)

goto :eof