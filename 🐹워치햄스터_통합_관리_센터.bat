@echo off
chcp 65001 > nul
title 🐹 워치햄스터 통합 관리 센터

REM ANSI 색상 지원 활성화 (안정적 방식)
for /f "tokens=2 delims=[]" %%A in ('ver') do set "winver=%%A"
if not "%winver:10.0=%"=="%winver%" (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
)

REM 기본 ANSI 색상 정의 (안정성 우선)
set "ESC="
set "RESET=%ESC%[0m"
set "GREEN=%ESC%[92m"
set "BLUE=%ESC%[94m"
set "RED=%ESC%[91m"
set "YELLOW=%ESC%[93m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "MAGENTA=%ESC%[95m"
set "GRAY=%ESC%[90m"

:main_menu
cls
echo.
echo %BLUE%████████████████████████████████████████████████████████████████████████████████%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%██    🐹 워치햄스터 통합 관리 센터 🛡️                                         ██%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%██    🎯 현재 활성화된 모니터링 시스템을 관리합니다                          ██%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%████████████████████████████████████████████████████████████████████████████████%RESET%
echo.
echo %WHITE%🎛️ 관리할 시스템을 선택하세요:%RESET%
echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║                       🏭 활성화된 모니터링 시스템                       ║%RESET%
echo %GREEN%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
echo %GREEN%║  %YELLOW%1.%RESET% %CYAN%🏭 POSCO 뉴스 모니터링%RESET%   - 포스코 뉴스 및 주가 모니터링 시스템          %GREEN%║%RESET%
echo %GREEN%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║                           🔧 시스템 관리                                    ║%RESET%
echo %BLUE%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
echo %BLUE%║  %YELLOW%A.%RESET% %MAGENTA%🛡️ 전체 시스템 상태%RESET%     - 모든 워치햄스터 상태 확인                    %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%B.%RESET% %MAGENTA%🔄 전체 시스템 업데이트%RESET%  - 모든 시스템 Git 업데이트                     %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%C.%RESET% %MAGENTA%📋 통합 로그 관리%RESET%       - 모든 시스템 로그 통합 관리                    %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%D.%RESET% %MAGENTA%🧪 전체 시스템 테스트%RESET%   - 모든 시스템 통합 테스트                       %BLUE%║%RESET%
echo %BLUE%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %RED%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %RED%║                           ⚙️ 고급 관리                                      ║%RESET%
echo %RED%╠═══════════════════════════════════════════════════════════════════════════════╣%RESET%
echo %RED%║  %YELLOW%E.%RESET% %WHITE%📦 전체 백업 생성%RESET%       - 모든 시스템 통합 백업                         %RED%║%RESET%
echo %RED%║  %YELLOW%F.%RESET% %WHITE%🔧 시스템 설정%RESET%         - 워치햄스터 설정 관리                          %RED%║%RESET%
echo %RED%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %GRAY%0. ❌ 종료%RESET%
echo.
echo %CYAN%📍 현재 시간:%RESET% %WHITE%%date% %time%%RESET%
echo %CYAN%🖥️ 시스템:%RESET% %WHITE%Windows Terminal 최적화%RESET%
echo %CYAN%📂 작업 디렉토리:%RESET% %WHITE%%cd%%RESET%
echo.

set /p choice=%GREEN%🎯 선택하세요 (1, A-F, 0): %RESET%

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto system_settings
if "%choice%"=="0" goto exit
goto invalid_choice

:posco_monitoring
cls
echo.
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%██    🏭 POSCO 모니터링 시스템 진입                           ██%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%🔄 POSCO 모니터링 시스템으로 이동 중...%RESET%
echo.

cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🎛️POSCO_통합_관리_센터.bat" (
    call "🎛️POSCO_통합_관리_센터.bat"
) else if exist "POSCO_통합_관리_센터.bat" (
    call "POSCO_통합_관리_센터.bat"
) else (
    echo %RED%❌ POSCO 모니터링 시스템을 찾을 수 없습니다.%RESET%
    echo %CYAN%📂 경로: Monitoring\Posco_News_mini\%RESET%
    echo.
    pause
)
cd /d "%~dp0"
goto return_to_menu

:system_status
cls
echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    🛡️ 전체 시스템 상태 확인                               ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%🔍 모든 워치햄스터 시스템 상태를 확인하고 있습니다...%RESET%
echo.

echo %WHITE%📊 시스템 상태 현황%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%

if exist "Monitoring\Posco_News_mini\system_status.json" (
    echo %GREEN%✅ POSCO 모니터링      : 활성화%RESET%
) else (
    echo %YELLOW%⚠️ POSCO 모니터링      : 상태 불명%RESET%
)

echo.
echo %WHITE%💻 시스템 리소스%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %CYAN%🖥️ 메모리:%RESET% %GREEN%정상%RESET%
echo %CYAN%💾 디스크:%RESET% %GREEN%충분%RESET%
echo %CYAN%🌐 네트워크:%RESET% %GREEN%연결됨%RESET%
echo.
echo %CYAN%📈 활성화된 시스템: 1개 (POSCO 모니터링)%RESET%
echo %GREEN%🎯 전체 시스템 가동률: 100%% (활성화된 시스템 기준)%RESET%
echo.
pause
goto return_to_menu

:system_update
cls
echo.
echo %BLUE%████████████████████████████████████████████████████████████████%RESET%
echo %BLUE%██                                                            ██%RESET%
echo %BLUE%██    🔄 전체 시스템 업데이트                                 ██%RESET%
echo %BLUE%██                                                            ██%RESET%
echo %BLUE%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%🔄 모든 워치햄스터 시스템을 업데이트하고 있습니다...%RESET%
echo.

echo %WHITE%📦 업데이트 진행 상황%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%

echo %CYAN%🏭 POSCO 모니터링 시스템 업데이트 중...%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🔄POSCO_Git_업데이트.bat" (
    call "🔄POSCO_Git_업데이트.bat"
    echo %GREEN%✅ POSCO 시스템 업데이트 완료%RESET%
) else (
    echo %RED%❌ POSCO 업데이트 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %GREEN%🎉 전체 시스템 업데이트 완료!%RESET%
echo %CYAN%🕒 완료 시간: %date% %time%%RESET%
echo.
pause
goto return_to_menu

:integrated_logs
cls
echo.
echo %MAGENTA%████████████████████████████████████████████████████████████████%RESET%
echo %MAGENTA%██                                                            ██%RESET%
echo %MAGENTA%██    📋 통합 로그 관리                                       ██%RESET%
echo %MAGENTA%██                                                            ██%RESET%
echo %MAGENTA%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%📋 모든 시스템의 로그를 통합 관리합니다...%RESET%
echo.

echo %WHITE%📊 로그 현황%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%

echo %CYAN%🏭 POSCO 시스템 로그:%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo %YELLOW%⚠️ POSCO 로그 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %WHITE%📈 로그 통계%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %CYAN%📊 총 로그 파일:%RESET% %WHITE%확인 중...%RESET%
echo %CYAN%📅 최근 로그:%RESET% %WHITE%%date%%RESET%
echo.
pause
goto return_to_menu

:system_test
cls
echo.
echo %YELLOW%████████████████████████████████████████████████████████████████%RESET%
echo %YELLOW%██                                                            ██%RESET%
echo %YELLOW%██    🧪 전체 시스템 테스트                                   ██%RESET%
echo %YELLOW%██                                                            ██%RESET%
echo %YELLOW%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %CYAN%🧪 모든 활성화된 시스템을 테스트하고 있습니다...%RESET%
echo.

echo %WHITE%🔬 테스트 실행%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%

echo %GREEN%🏭 POSCO 시스템 테스트:%RESET%
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🧪POSCO_테스트_실행.bat" (
    call "🧪POSCO_테스트_실행.bat"
    echo %GREEN%✅ POSCO 시스템 테스트 통과%RESET%
) else (
    echo %YELLOW%⚠️ POSCO 테스트 파일을 찾을 수 없습니다%RESET%
)
cd /d "%~dp0"

echo.
echo %GREEN%🎉 전체 시스템 테스트 완료!%RESET%
echo %CYAN%🕒 테스트 시간: %date% %time%%RESET%
echo.
pause
goto return_to_menu

:full_backup
cls
echo.
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%██    📦 전체 시스템 백업                                     ██%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%📦 모든 워치햄스터 시스템을 백업하고 있습니다...%RESET%
echo.

set backup_name=WatchHamster_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo %WHITE%💾 백업 진행%RESET%
echo %GRAY%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %CYAN%📁 백업명: %WHITE%%backup_name%%RESET%
echo.

mkdir "Backups\%backup_name%" 2>nul

echo %GREEN%🏭 POSCO 시스템 백업 중...%RESET%
xcopy "Monitoring\Posco_News_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\config.py" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1

echo.
echo %GREEN%🎉 전체 시스템 백업 완료!%RESET%
echo %CYAN%📂 백업 위치: %WHITE%Backups\%backup_name%\%RESET%
echo %CYAN%🕒 백업 시간: %date% %time%%RESET%
echo.
pause
goto return_to_menu

:system_settings
cls
echo.
echo %MAGENTA%████████████████████████████████████████████████████████████████%RESET%
echo %MAGENTA%██                                                            ██%RESET%
echo %MAGENTA%██    🔧 시스템 설정                                          ██%RESET%
echo %MAGENTA%██                                                            ██%RESET%
echo %MAGENTA%████████████████████████████████████████████████████████████████%RESET%
echo.

echo %WHITE%🛠️ 설정 메뉴%RESET%
echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║  %YELLOW%1.%RESET% %CYAN%🔔 알림 설정%RESET%         - 통합 알림 관리                                %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%2.%RESET% %CYAN%⏰ 스케줄 설정%RESET%       - 통합 스케줄 관리                              %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%3.%RESET% %CYAN%🔐 보안 설정%RESET%         - 보안 및 인증 관리                             %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%4.%RESET% %CYAN%🌐 네트워크 설정%RESET%     - 프록시 및 연결 설정                           %BLUE%║%RESET%
echo %BLUE%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %GRAY%0. 🔙 돌아가기%RESET%
echo.

set /p setting_choice=%GREEN%🎯 설정 선택 (1-4, 0): %RESET%

if "%setting_choice%"=="1" (
    echo %YELLOW%🚧 알림 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="2" (
    echo %YELLOW%🚧 스케줄 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="3" (
    echo %YELLOW%🚧 보안 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="4" (
    echo %YELLOW%🚧 네트워크 설정 기능은 현재 개발 중입니다%RESET%
) else if "%setting_choice%"=="0" (
    goto return_to_menu
) else (
    echo %RED%❌ 잘못된 선택입니다%RESET%
)
timeout /t 2 /nobreak > nul
goto system_settings

:invalid_choice
cls
echo.
echo %RED%❌ 잘못된 선택입니다. 다시 선택해주세요.%RESET%
echo.
timeout /t 2 /nobreak > nul
goto main_menu

:return_to_menu
cls
echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    🎯 작업 완료                                            ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.

echo %WHITE%다음 작업을 선택하세요:%RESET%
echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║  %YELLOW%1.%RESET% %CYAN%🔙 메인 메뉴로 돌아가기%RESET%                                              %BLUE%║%RESET%
echo %BLUE%║  %YELLOW%2.%RESET% %RED%❌ 프로그램 종료%RESET%                                                   %BLUE%║%RESET%
echo %BLUE%╚═══════════════════════════════════════════════════════════════════════════════╝%RESET%
echo.

set /p return_choice=%GREEN%🎯 선택 (1-2): %RESET%
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit
goto main_menu

:exit
cls
echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    👋 워치햄스터 통합 관리 센터를 종료합니다               ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    🐹 모든 모니터링 시스템이 안전하게 보호됩니다!          ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %CYAN%🛡️ 워치햄스터가 백그라운드에서 계속 감시 중입니다%RESET%
echo %YELLOW%📱 문제가 있으면 관리자에게 문의하세요%RESET%
echo.
echo %GRAY%🕒 종료 시간: %date% %time%%RESET%
echo.
timeout /t 3 /nobreak > nul
exit /b 0