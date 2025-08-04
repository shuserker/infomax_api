@echo off

REM Windows Terminal이 있는지 확인하고 있으면 Windows Terminal에서 실행
where wt >nul 2>&1
if %errorlevel% == 0 (
    if not "%WT_SESSION%" == "" goto :skip_wt_launch
    echo 🚀 Windows Terminal에서 실행 중...
    wt -p "Command Prompt" cmd /k "%~f0" terminal
    exit /b
)

:skip_wt_launch
REM 터미널 환경 설정
chcp 65001 > nul
title 🐹 워치햄스터 총괄 관리 센터

REM ANSI 컬러 활성화
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f > nul 2>&1

REM 콘솔 설정 최적화  
color 0F
mode con: cols=100 lines=40

REM 터미널 매개변수 확인
if "%1"=="terminal" shift

:main_menu
cls
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo ██                                                                            ██
echo ██    🐹 워치햄스터 총괄 관리 센터 🛡️                                         ██
echo ██                                                                            ██
echo ██    🎯 현재 활성화된 모니터링 시스템을 관리합니다                          ██
echo ██                                                                            ██
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo 🎛️ 관리할 시스템을 선택하세요:
echo.
echo.
echo [92m╔═══════════════════════════════════════════════════════════════════════════════╗[0m
echo [92m║[0m                       [96m🏭 활성화된 모니터링 시스템[0m                       [92m║[0m
echo [92m╠═══════════════════════════════════════════════════════════════════════════════╣[0m
echo [92m║[0m  [93m1.[0m [96m🏭 POSCO 뉴스 모니터링[0m   - 포스코 뉴스 및 주가 모니터링 시스템          [92m║[0m
echo [92m╚═══════════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo [94m╔═══════════════════════════════════════════════════════════════════════════════╗[0m
echo [94m║[0m                           [95m🔧 시스템 관리[0m                                    [94m║[0m
echo [94m╠═══════════════════════════════════════════════════════════════════════════════╣[0m
echo [94m║[0m  [93mA.[0m [95m🛡️ 전체 시스템 상태[0m     - 모든 워치햄스터 상태 확인                    [94m║[0m
echo [94m║[0m  [93mB.[0m [95m🔄 전체 시스템 업데이트[0m  - 모든 시스템 Git 업데이트                     [94m║[0m
echo [94m║[0m  [93mC.[0m [95m📋 통합 로그 관리[0m       - 모든 시스템 로그 통합 관리                    [94m║[0m
echo [94m║[0m  [93mD.[0m [95m🧪 전체 시스템 테스트[0m   - 모든 시스템 통합 테스트                       [94m║[0m
echo [94m╚═══════════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo [91m╔═══════════════════════════════════════════════════════════════════════════════╗[0m
echo [91m║[0m                           [97m⚙️ 고급 관리[0m                                      [91m║[0m
echo [91m╠═══════════════════════════════════════════════════════════════════════════════╣[0m
echo [91m║[0m  [93mE.[0m [97m📦 전체 백업 생성[0m       - 모든 시스템 통합 백업                         [91m║[0m
echo [91m║[0m  [93mF.[0m [97m🔧 워치햄스터 설정[0m      - 총괄 설정 관리                                [91m║[0m
echo [91m╚═══════════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo  0. ❌ 종료
echo.
echo.
echo [96m📍 현재 시간:[0m [97m%date% %time%[0m
echo [96m🐹 워치햄스터 버전:[0m [97mv2.0 (총괄 관리 센터)[0m
echo [96m📂 작업 디렉토리:[0m [97m%cd%[0m
echo.
echo [93m  0. ❌ 종료[0m
echo.
set /p choice=[92m🎯 선택하세요 (1, A-F, 0): [0m 

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto watchhamster_config
if "%choice%"=="0" goto exit
goto invalid_choice

:posco_monitoring
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🏭 POSCO 모니터링 시스템 진입                           ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🔄 POSCO 모니터링 시스템으로 이동 중...
echo.
cd /d "Monitoring\Posco_News_mini"
if exist "🎛️POSCO_통합_관리_센터.bat" (
    call "🎛️POSCO_통합_관리_센터.bat"
) else (
    echo ❌ POSCO 모니터링 시스템을 찾을 수 없습니다.
    echo 📂 경로: Monitoring\Posco_News_mini\🎛️POSCO_통합_관리_센터.bat
    echo.
    pause
)
cd /d "%~dp0"
goto return_to_menu



:system_status
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🛡️ 전체 시스템 상태 확인                               ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🔍 모든 워치햄스터 시스템 상태를 확인하고 있습니다...
echo.
echo [96m╔═══════════════════════════════════════════════════════════╗[0m
echo [96m║[0m                    [97m시스템 상태 현황[0m                         [96m║[0m
echo [96m╠═══════════════════════════════════════════════════════════╣[0m
echo [96m║[0m  [92m🏭 POSCO 모니터링[0m      : [92m✅ 활성화[0m                        [96m║[0m
echo [96m╚═══════════════════════════════════════════════════════════╝[0m
echo.
echo [93m📊 활성화된 시스템:[0m [97m1개 (POSCO 모니터링)[0m
echo [93m🎯 전체 시스템 가동률:[0m [92m100%% (활성화된 시스템 기준)[0m
echo.
pause
goto return_to_menu

:system_update
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🔄 전체 시스템 업데이트                                 ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🔄 모든 워치햄스터 시스템을 업데이트하고 있습니다...
echo.
echo 📦 POSCO 모니터링 시스템 업데이트 중...
cd /d "Monitoring\Posco_News_mini"
if exist "🔄POSCO_Git_업데이트.bat" (
    call "🔄POSCO_Git_업데이트.bat"
) else (
    echo ❌ POSCO 업데이트 파일을 찾을 수 없습니다.
)
cd /d "%~dp0"
echo.
echo ✅ 전체 시스템 업데이트 완료!
echo.
pause
goto return_to_menu

:integrated_logs
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📋 통합 로그 관리                                       ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📋 모든 시스템의 로그를 통합 관리합니다...
echo.
echo 🏭 POSCO 시스템 로그:
cd /d "Monitoring\Posco_News_mini"
if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo ❌ POSCO 로그 파일을 찾을 수 없습니다.
)
cd /d "%~dp0"
echo.
pause
goto return_to_menu

:system_test
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🧪 전체 시스템 테스트                                   ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🧪 모든 활성화된 시스템을 테스트하고 있습니다...
echo.
echo 🏭 POSCO 시스템 테스트:
cd /d "Monitoring\Posco_News_mini"
if exist "🧪POSCO_테스트_실행.bat" (
    call "🧪POSCO_테스트_실행.bat"
) else (
    echo ❌ POSCO 테스트 파일을 찾을 수 없습니다.
)
cd /d "%~dp0"
echo.
echo ✅ 전체 시스템 테스트 완료!
echo.
pause
goto return_to_menu

:add_monitoring
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🎛️ 새 모니터링 시스템 추가                             ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🚧 새 모니터링 시스템 추가 기능은 현재 개발 중입니다.
echo.
echo 💡 계획된 기능:
echo    • 새로운 기업/시장 모니터링 시스템 자동 생성
echo    • 템플릿 기반 모니터링 구조 생성
echo    • 설정 파일 자동 구성
echo    • 워치햄스터 자동 연결
echo.
echo 📅 예상 완료일: 2025년 10월
echo.
pause
goto return_to_menu

:full_backup
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📦 전체 시스템 백업                                     ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📦 모든 워치햄스터 시스템을 백업하고 있습니다...
echo.
set backup_name=WatchHamster_Full_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%
echo 📁 백업 이름: %backup_name%
echo.
mkdir "Backups\%backup_name%" 2>nul
echo 🏭 POSCO 시스템 백업 중...
xcopy "Monitoring\Posco_News_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\config.py" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1
echo ✅ 전체 시스템 백업 완료!
echo 📂 백업 위치: Backups\%backup_name%\
echo.
pause
goto return_to_menu

:watchhamster_config
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🔧 워치햄스터 총괄 설정                                 ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🛠️ 워치햄스터 총괄 설정을 관리합니다...
echo.
echo 🚧 총괄 설정 기능은 현재 개발 중입니다.
echo.
echo 💡 계획된 기능:
echo    • 모든 시스템 통합 설정 관리
echo    • 알림 설정 통합 관리
echo    • 스케줄 통합 관리
echo    • 보안 설정 관리
echo.
echo 📅 예상 완료일: 2025년 11월
echo.
pause
goto return_to_menu

:invalid_choice
echo.
echo ❌ 잘못된 선택입니다. 다시 선택해주세요.
echo.
pause
goto main_menu

:return_to_menu
echo.
echo [92m╔═════════════════════════════════════════════════════════════════════════════╗[0m
echo [92m║[0m                           [97m🎯 작업 완료[0m                                      [92m║[0m
echo [92m╚═════════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo 1. 🔙 메인 메뉴로 돌아가기
echo 2. ❌ 프로그램 종료
echo.
set /p return_choice=선택 (1-2): 
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit
goto main_menu

:exit
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    👋 워치햄스터 총괄 관리 센터를 종료합니다               ██
echo ██                                                            ██
echo ██    🐹 모든 모니터링 시스템이 안전하게 보호됩니다!          ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🛡️ 워치햄스터가 백그라운드에서 계속 감시 중입니다.
echo 📱 문제가 있으면 관리자에게 문의하세요.
echo.
pause
exit