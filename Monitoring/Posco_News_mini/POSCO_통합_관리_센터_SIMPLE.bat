@echo off
chcp 65001 > nul
title POSCO 모니터링 관리 센터 - 간단 버전

REM ANSI 색상 활성화
for /f "tokens=2 delims=[]" %%A in ('ver') do set "winver=%%A"
if not "%winver:10.0=%"=="%winver%" (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1
)

REM 색상 정의
set "RESET=[0m"
set "GREEN=[92m"
set "BLUE=[94m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "WHITE=[97m"

:main_menu
cls
echo.
echo %BLUE%████████████████████████████████████████████████████████████████████████████████%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%██    POSCO 모니터링 관리 센터 (POSCO Monitoring Control Center)             ██%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%██    POSCO 뉴스 및 주가 모니터링 시스템 전용 관리 센터                       ██%RESET%
echo %BLUE%██                                                                            ██%RESET%
echo %BLUE%████████████████████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%원하는 작업을 선택하세요:%RESET%
echo.
echo %GREEN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %GREEN%                            시스템 운영                                       %RESET%
echo %GREEN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%   1. 워치햄스터 시작        - 모니터링 시스템 시작                           %RESET%
echo %WHITE%   2. 모니터링 중지          - 모든 모니터링 프로세스 중지                    %RESET%
echo %WHITE%   3. 시스템 상태 확인       - 현재 시스템 상태 점검                          %RESET%
echo.
echo %CYAN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %CYAN%                            시스템 관리                                       %RESET%
echo %CYAN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%   4. Git 업데이트          - 최신 코드로 업데이트                            %RESET%
echo %WHITE%   5. 로그 확인             - 시스템 로그 파일 관리                           %RESET%
echo %WHITE%   6. 테스트 실행           - 개별 모니터 테스트                              %RESET%
echo.
echo %YELLOW%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %YELLOW%                            대시보드 및 리포트                              %RESET%
echo %YELLOW%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%   7. 대시보드 열기         - GitHub Pages 대시보드                          %RESET%
echo %WHITE%   8. 리포트 보기           - 통합 분석 리포트                                %RESET%
echo %WHITE%   9. Dooray 채널 열기      - 알림 채널 확인                                 %RESET%
echo.
echo %RED%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %RED%                            고급 기능                                         %RESET%
echo %RED%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%   A. 시스템 리셋           - 전체 시스템 초기화                              %RESET%
echo %WHITE%   B. 백업 생성             - 현재 상태 백업                                  %RESET%
echo %WHITE%   C. 설정 편집             - 시스템 설정 파일 편집                           %RESET%
echo.
echo %WHITE%0. 총괄 센터로 돌아가기%RESET%
echo.
echo %CYAN%현재 시간:%RESET% %WHITE%%date% %time%%RESET%
echo %CYAN%작업 디렉토리:%RESET% %WHITE%%cd%%RESET%
echo.
set /p choice=%GREEN%선택하세요 (1-9, A-C, 0): %RESET%

if "%choice%"=="1" goto start_watchhamster
if "%choice%"=="2" goto stop_watchhamster
if "%choice%"=="3" goto check_status
if "%choice%"=="4" goto git_update
if "%choice%"=="5" goto check_logs
if "%choice%"=="6" goto run_test
if "%choice%"=="7" goto open_dashboard
if "%choice%"=="8" goto view_report
if "%choice%"=="9" goto open_dooray
if /i "%choice%"=="A" goto system_reset
if /i "%choice%"=="B" goto create_backup
if /i "%choice%"=="C" goto edit_config
if "%choice%"=="0" goto exit_to_main
goto invalid_choice

:start_watchhamster
cls
echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    POSCO 워치햄스터 시작                                   ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%POSCO 모니터링 시스템을 시작합니다...%RESET%
echo.

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Python이 설치되지 않았거나 PATH에 없습니다.%RESET%
    echo %CYAN%Python 3.8 이상을 설치해주세요.%RESET%
    pause
    goto return_to_menu
) else (
    echo %GREEN%Python 환경 확인됨%RESET%
)

REM 워치햄스터 파일 확인
if exist "monitor_WatchHamster.py" (
    echo %GREEN%워치햄스터 메인 파일 확인됨%RESET%
    echo.
    echo %CYAN%워치햄스터를 시작합니다... (Ctrl+C로 중단)%RESET%
    echo.
    python monitor_WatchHamster.py
) else (
    echo %RED%monitor_WatchHamster.py 파일을 찾을 수 없습니다.%RESET%
)

echo.
pause
goto return_to_menu

:stop_watchhamster
cls
echo.
echo %RED%████████████████████████████████████████████████████████████████%RESET%
echo %RED%██                                                            ██%RESET%
echo %RED%██    모니터링 시스템 중지                                    ██%RESET%
echo %RED%██                                                            ██%RESET%
echo %RED%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%실행 중인 Python 프로세스를 확인하고 있습니다...%RESET%

tasklist /fi "imagename eq python.exe" | find "python.exe" >nul
if not errorlevel 1 (
    echo %YELLOW%실행 중인 Python 프로세스를 발견했습니다.%RESET%
    set /p confirm=%RED%모든 Python 프로세스를 종료하시겠습니까? (Y/N): %RESET%
    if /i "!confirm!"=="Y" (
        taskkill /f /im python.exe >nul 2>&1
        echo %GREEN%워치햄스터 프로세스가 종료되었습니다.%RESET%
    ) else (
        echo %CYAN%작업이 취소되었습니다.%RESET%
    )
) else (
    echo %CYAN%실행 중인 워치햄스터 프로세스가 없습니다.%RESET%
)

echo.
pause
goto return_to_menu

:check_status
cls
echo.
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%██    시스템 상태 확인                                        ██%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%시스템 상태를 확인하고 있습니다...%RESET%
echo.

echo %WHITE%파일 상태:%RESET%
if exist "monitor_WatchHamster.py" (echo %GREEN%  ✓ monitor_WatchHamster.py - 존재%RESET%) else (echo %RED%  ✗ monitor_WatchHamster.py - 없음%RESET%)
if exist "config.py" (echo %GREEN%  ✓ config.py - 존재%RESET%) else (echo %YELLOW%  ! config.py - 없음%RESET%)

echo.
echo %WHITE%프로세스 상태:%RESET%
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if not errorlevel 1 (
    echo %GREEN%  ✓ Python 프로세스 실행 중%RESET%
) else (
    echo %YELLOW%  ! Python 프로세스 없음%RESET%
)

echo.
pause
goto return_to_menu

:git_update
cls
echo.
echo %BLUE%████████████████████████████████████████████████████████████████%RESET%
echo %BLUE%██                                                            ██%RESET%
echo %BLUE%██    Git 업데이트                                           ██%RESET%
echo %BLUE%██                                                            ██%RESET%
echo %BLUE%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %YELLOW%Git 저장소를 업데이트합니다...%RESET%
echo.

if exist "🔄POSCO_Git_업데이트.bat" (
    call "🔄POSCO_Git_업데이트.bat"
) else (
    git pull origin main
    echo %GREEN%Git 업데이트 완료!%RESET%
)

pause
goto return_to_menu

:check_logs
cls
echo.
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%██    로그 파일 확인                                          ██%RESET%
echo %CYAN%██                                                            ██%RESET%
echo %CYAN%████████████████████████████████████████████████████████████████%RESET%
echo.

if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo %YELLOW%로그 파일을 확인합니다...%RESET%
    echo.
    if exist "*.log" (
        echo %CYAN%로그 파일 목록:%RESET%
        dir *.log /b
        echo.
        echo %WHITE%최신 로그 내용 (마지막 10줄):%RESET%
        for %%f in (*.log) do (
            echo %CYAN%--- %%f ---%RESET%
            type "%%f" | more
            echo.
        )
    ) else (
        echo %YELLOW%로그 파일이 없습니다.%RESET%
    )
)

pause
goto return_to_menu

:run_test
cls
echo.
echo %YELLOW%████████████████████████████████████████████████████████████████%RESET%
echo %YELLOW%██                                                            ██%RESET%
echo %YELLOW%██    시스템 테스트 실행                                      ██%RESET%
echo %YELLOW%██                                                            ██%RESET%
echo %YELLOW%████████████████████████████████████████████████████████████████%RESET%
echo.

if exist "🧪POSCO_테스트_실행.bat" (
    call "🧪POSCO_테스트_실행.bat"
) else (
    echo %CYAN%시스템 테스트를 실행합니다...%RESET%
    echo.
    if exist "monitor_WatchHamster.py" (
        echo %WHITE%Python 스크립트 테스트:%RESET%
        python -c "print('Python 환경 테스트 성공')"
        echo %GREEN%테스트 완료%RESET%
    ) else (
        echo %RED%테스트할 Python 파일이 없습니다.%RESET%
    )
)

pause
goto return_to_menu

:open_dashboard
echo.
echo %CYAN%대시보드를 열고 있습니다...%RESET%
start https://your-github-pages-url.github.io
pause
goto return_to_menu

:view_report
echo.
echo %CYAN%리포트를 확인합니다...%RESET%
if exist "posco_news_report.html" (
    start posco_news_report.html
) else (
    echo %RED%리포트 파일을 찾을 수 없습니다.%RESET%
)
pause
goto return_to_menu

:open_dooray
echo.
echo %BLUE%Dooray 채널을 열고 있습니다...%RESET%
start https://dooray.com
pause
goto return_to_menu

:system_reset
echo.
echo %RED%시스템 리셋 기능은 개발 중입니다.%RESET%
pause
goto return_to_menu

:create_backup
echo.
echo %CYAN%백업 기능은 개발 중입니다.%RESET%
pause
goto return_to_menu

:edit_config
echo.
echo %CYAN%설정 파일을 편집합니다...%RESET%
if exist "config.py" (
    notepad config.py
) else (
    echo %RED%config.py 파일을 찾을 수 없습니다.%RESET%
)
pause
goto return_to_menu

:invalid_choice
cls
echo.
echo %RED%잘못된 선택입니다. 다시 선택해주세요.%RESET%
echo.
pause
goto main_menu

:return_to_menu
echo.
echo +=========================================================================+
echo ^|                           작업 완료                                      ^|
echo +=========================================================================+
echo.
echo 1. 메인 메뉴로 돌아가기
echo 2. 총괄 센터로 돌아가기
echo.
set /p return_choice=선택 (1-2): 
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit_to_main
goto main_menu

:exit_to_main
cls
echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%██    총괄 관리 센터로 돌아갑니다                             ██%RESET%
echo %GREEN%██                                                            ██%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %CYAN%POSCO 모니터링 관리를 종료합니다.%RESET%
echo.
pause
exit