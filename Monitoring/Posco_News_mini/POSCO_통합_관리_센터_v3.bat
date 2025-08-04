@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title POSCO 모니터링 관리 센터

REM 안전한 색상 시스템 (이모지 제거)
set "C_RESET=[0m"
set "C_GREEN=[92m"
set "C_BLUE=[94m"
set "C_RED=[91m"
set "C_YELLOW=[93m"
set "C_CYAN=[96m"
set "C_WHITE=[97m"
set "C_MAGENTA=[95m"

:main_menu
cls
echo.
echo !C_BLUE!████████████████████████████████████████████████████████████████████████████████!C_RESET!
echo !C_BLUE!██                                                                            ██!C_RESET!
echo !C_BLUE!██    POSCO 모니터링 관리 센터 (POSCO Monitoring Control Center)             ██!C_RESET!
echo !C_BLUE!██                                                                            ██!C_RESET!
echo !C_BLUE!██    POSCO 뉴스 및 주가 모니터링 시스템 전용 관리 센터                       ██!C_RESET!
echo !C_BLUE!██                                                                            ██!C_RESET!
echo !C_BLUE!████████████████████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!원하는 작업을 선택하세요:!C_RESET!
echo.
echo !C_GREEN!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_GREEN!                            시스템 운영                                       !C_RESET!
echo !C_GREEN!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_WHITE!   1. 워치햄스터 시작        - 모니터링 시스템 시작                           !C_RESET!
echo !C_WHITE!   2. 모니터링 중지          - 모든 모니터링 프로세스 중지                    !C_RESET!
echo !C_WHITE!   3. 시스템 상태 확인       - 현재 시스템 상태 점검                          !C_RESET!
echo.
echo !C_CYAN!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_CYAN!                            시스템 관리                                       !C_RESET!
echo !C_CYAN!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_WHITE!   4. Git 업데이트          - 최신 코드로 업데이트                            !C_RESET!
echo !C_WHITE!   5. 로그 확인             - 시스템 로그 파일 관리                           !C_RESET!
echo !C_WHITE!   6. 테스트 실행           - 개별 모니터 테스트                              !C_RESET!
echo.
echo !C_MAGENTA!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_MAGENTA!                            대시보드 및 리포트                              !C_RESET!
echo !C_MAGENTA!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_WHITE!   7. 대시보드 열기         - GitHub Pages 대시보드                          !C_RESET!
echo !C_WHITE!   8. 리포트 보기           - 통합 분석 리포트                                !C_RESET!
echo !C_WHITE!   9. Dooray 채널 열기      - 알림 채널 확인                                 !C_RESET!
echo.
echo !C_RED!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_RED!                            고급 기능                                         !C_RESET!
echo !C_RED!═══════════════════════════════════════════════════════════════════════════════!C_RESET!
echo !C_WHITE!   A. 시스템 리셋           - 전체 시스템 초기화                              !C_RESET!
echo !C_WHITE!   B. 백업 생성             - 현재 상태 백업                                  !C_RESET!
echo !C_WHITE!   C. 설정 편집             - 시스템 설정 파일 편집                           !C_RESET!
echo.
echo !C_WHITE!0. 종료!C_RESET!
echo.
echo !C_CYAN!현재 시간:!C_RESET! !C_WHITE!%date% %time%!C_RESET!
echo !C_CYAN!작업 디렉토리:!C_RESET! !C_WHITE!%cd%!C_RESET!
echo.
set /p choice=!C_GREEN!선택하세요 (1-9, A-C, 0): !C_RESET!

if "%choice%"=="1" goto start_monitoring
if "%choice%"=="2" goto stop_monitoring
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
if "%choice%"=="0" goto exit
goto invalid_choice

:start_monitoring
echo.
echo !C_GREEN!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_GREEN!██                                                            ██!C_RESET!
echo !C_GREEN!██    워치햄스터 모니터링 시작                                ██!C_RESET!
echo !C_GREEN!██                                                            ██!C_RESET!
echo !C_GREEN!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!POSCO 모니터링 시스템을 시작합니다...!C_RESET!
echo.
if exist "Posco_News_mini.py" (
    echo !C_CYAN!Python 스크립트를 실행합니다...!C_RESET!
    python Posco_News_mini.py
) else (
    echo !C_RED!Posco_News_mini.py 파일을 찾을 수 없습니다.!C_RESET!
)
echo.
pause
goto main_menu

:stop_monitoring
echo.
echo !C_RED!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_RED!██                                                            ██!C_RESET!
echo !C_RED!██    모니터링 시스템 중지                                    ██!C_RESET!
echo !C_RED!██                                                            ██!C_RESET!
echo !C_RED!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!실행 중인 Python 프로세스를 종료합니다...!C_RESET!
taskkill /f /im python.exe 2>nul
echo !C_GREEN!모니터링 시스템이 중지되었습니다.!C_RESET!
echo.
pause
goto main_menu

:check_status
echo.
echo !C_CYAN!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_CYAN!██                                                            ██!C_RESET!
echo !C_CYAN!██    시스템 상태 확인                                        ██!C_RESET!
echo !C_CYAN!██                                                            ██!C_RESET!
echo !C_CYAN!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!시스템 상태를 확인하고 있습니다...!C_RESET!
echo.
echo !C_WHITE!파일 상태:!C_RESET!
if exist "Posco_News_mini.py" (echo !C_GREEN!  ✓ Posco_News_mini.py - 존재!C_RESET!) else (echo !C_RED!  ✗ Posco_News_mini.py - 없음!C_RESET!)
if exist "config.py" (echo !C_GREEN!  ✓ config.py - 존재!C_RESET!) else (echo !C_RED!  ✗ config.py - 없음!C_RESET!)
if exist "posco_news_data.json" (echo !C_GREEN!  ✓ posco_news_data.json - 존재!C_RESET!) else (echo !C_YELLOW!  ! posco_news_data.json - 없음 (정상)!C_RESET!)
echo.
echo !C_WHITE!프로세스 상태:!C_RESET!
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if !errorlevel! equ 0 (
    echo !C_GREEN!  ✓ Python 프로세스 실행 중!C_RESET!
) else (
    echo !C_YELLOW!  ! Python 프로세스 없음!C_RESET!
)
echo.
pause
goto main_menu

:git_update
echo.
echo !C_BLUE!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_BLUE!██                                                            ██!C_RESET!
echo !C_BLUE!██    Git 업데이트                                           ██!C_RESET!
echo !C_BLUE!██                                                            ██!C_RESET!
echo !C_BLUE!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!Git 저장소를 업데이트합니다...!C_RESET!
echo.
git pull origin main
echo.
echo !C_GREEN!Git 업데이트 완료!C_RESET!
pause
goto main_menu

:check_logs
echo.
echo !C_MAGENTA!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_MAGENTA!██                                                            ██!C_RESET!
echo !C_MAGENTA!██    로그 파일 확인                                          ██!C_RESET!
echo !C_MAGENTA!██                                                            ██!C_RESET!
echo !C_MAGENTA!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!로그 파일을 확인합니다...!C_RESET!
echo.
if exist "*.log" (
    echo !C_CYAN!로그 파일 목록:!C_RESET!
    dir *.log /b
    echo.
    echo !C_WHITE!최신 로그 내용 (마지막 10줄):!C_RESET!
    for %%f in (*.log) do (
        echo !C_CYAN!--- %%f ---!C_RESET!
        powershell "Get-Content '%%f' | Select-Object -Last 10"
        echo.
    )
) else (
    echo !C_YELLOW!로그 파일이 없습니다.!C_RESET!
)
pause
goto main_menu

:run_test
echo.
echo !C_YELLOW!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_YELLOW!██                                                            ██!C_RESET!
echo !C_YELLOW!██    시스템 테스트 실행                                      ██!C_RESET!
echo !C_YELLOW!██                                                            ██!C_RESET!
echo !C_YELLOW!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_CYAN!시스템 테스트를 실행합니다...!C_RESET!
echo.
if exist "Posco_News_mini.py" (
    echo !C_WHITE!Python 스크립트 테스트 실행:!C_RESET!
    python -c "import Posco_News_mini; print('모듈 로드 성공')"
) else (
    echo !C_RED!테스트할 Python 파일이 없습니다.!C_RESET!
)
echo.
pause
goto main_menu

:open_dashboard
echo.
echo !C_CYAN!대시보드를 열고 있습니다...!C_RESET!
start https://your-github-pages-url.github.io
pause
goto main_menu

:view_report
echo.
echo !C_MAGENTA!리포트를 확인합니다...!C_RESET!
if exist "posco_news_report.html" (
    start posco_news_report.html
) else (
    echo !C_RED!리포트 파일을 찾을 수 없습니다.!C_RESET!
)
pause
goto main_menu

:open_dooray
echo.
echo !C_BLUE!Dooray 채널을 열고 있습니다...!C_RESET!
start https://dooray.com
pause
goto main_menu

:system_reset
echo.
echo !C_RED!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_RED!██                                                            ██!C_RESET!
echo !C_RED!██    시스템 리셋 (주의!)                                     ██!C_RESET!
echo !C_RED!██                                                            ██!C_RESET!
echo !C_RED!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_YELLOW!경고: 이 작업은 모든 데이터를 초기화합니다.!C_RESET!
set /p confirm=!C_RED!정말 계속하시겠습니까? (Y/N): !C_RESET!
if /i "%confirm%"=="Y" (
    echo !C_YELLOW!시스템을 리셋합니다...!C_RESET!
    del *.json 2>nul
    del *.log 2>nul
    echo !C_GREEN!시스템 리셋 완료!C_RESET!
) else (
    echo !C_CYAN!리셋이 취소되었습니다.!C_RESET!
)
pause
goto main_menu

:create_backup
echo.
echo !C_CYAN!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_CYAN!██                                                            ██!C_RESET!
echo !C_CYAN!██    백업 생성                                               ██!C_RESET!
echo !C_CYAN!██                                                            ██!C_RESET!
echo !C_CYAN!████████████████████████████████████████████████████████████████!C_RESET!
echo.
set backup_name=POSCO_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%
echo !C_YELLOW!백업을 생성합니다: %backup_name%!C_RESET!
mkdir "Backups\%backup_name%" 2>nul
xcopy "*.json" "Backups\%backup_name%\" /Q 2>nul
xcopy "*.log" "Backups\%backup_name%\" /Q 2>nul
xcopy "*.py" "Backups\%backup_name%\" /Q 2>nul
echo !C_GREEN!백업 완료: Backups\%backup_name%\!C_RESET!
pause
goto main_menu

:edit_config
echo.
echo !C_MAGENTA!설정 파일을 편집합니다...!C_RESET!
if exist "config.py" (
    notepad config.py
) else (
    echo !C_RED!config.py 파일을 찾을 수 없습니다.!C_RESET!
)
pause
goto main_menu

:invalid_choice
echo.
echo !C_RED!잘못된 선택입니다. 다시 선택해주세요.!C_RESET!
echo.
pause
goto main_menu

:exit
echo.
echo !C_GREEN!████████████████████████████████████████████████████████████████!C_RESET!
echo !C_GREEN!██                                                            ██!C_RESET!
echo !C_GREEN!██    POSCO 모니터링 관리 센터를 종료합니다                   ██!C_RESET!
echo !C_GREEN!██                                                            ██!C_RESET!
echo !C_GREEN!████████████████████████████████████████████████████████████████!C_RESET!
echo.
echo !C_CYAN!안전하게 종료되었습니다.!C_RESET!
echo.
pause
exit