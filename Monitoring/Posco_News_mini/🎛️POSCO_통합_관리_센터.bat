@echo off
chcp 65001 > nul
title POSCO 모니터링 관리 센터

:main_menu
cls
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo ██                                                                            ██
echo ██    🏭 POSCO 모니터링 관리 센터 🏢                                          ██
echo ██                                                                            ██
echo ██    📊 POSCO 뉴스 및 주가 모니터링 시스템 전용 관리 센터                   ██
echo ██                                                                            ██
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo 🎯 원하는 작업을 선택하세요:
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo                            🚀 시스템 운영                                    
echo ═══════════════════════════════════════════════════════════════════════════════
echo   1. 🚀 워치햄스터 시작        - 모니터링 시스템 시작                        
echo   2. 🛑 모니터링 중지          - 모든 모니터링 프로세스 중지                 
echo   3. 📊 시스템 상태 확인       - 현재 시스템 상태 점검                       
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo                            🔧 시스템 관리                                    
echo ═══════════════════════════════════════════════════════════════════════════════
echo   4. 🔄 Git 업데이트          - 최신 코드로 업데이트                         
echo   5. 📋 로그 확인             - 시스템 로그 파일 관리                        
echo   6. 🧪 테스트 실행           - 개별 모니터 테스트                           
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo                            📊 대시보드 & 리포트                              
echo ═══════════════════════════════════════════════════════════════════════════════
echo   7. 🌐 대시보드 열기         - GitHub Pages 대시보드                       
echo   8. 📈 리포트 보기           - 통합 분석 리포트                             
echo   9. 📱 Dooray 채널 열기      - 알림 채널 확인                              
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo                            ⚙️ 고급 기능                                      
echo ═══════════════════════════════════════════════════════════════════════════════
echo   A. 🔧 시스템 리셋           - 전체 시스템 초기화                           
echo   B. 📦 백업 생성             - 현재 상태 백업                               
echo   C. 🛠️ 설정 편집             - 시스템 설정 파일 편집
echo.
echo  0. ❌ 종료
echo.
echo 📍 현재 시간: %date% %time%
echo 📂 작업 디렉토리: %cd%
echo.
set /p choice=🎯 선택하세요 (1-9, A-C, 0): 

if "%choice%"=="1" goto start_watchhamster
if "%choice%"=="2" goto stop_monitoring
if "%choice%"=="3" goto check_status
if "%choice%"=="4" goto git_update
if "%choice%"=="5" goto check_logs
if "%choice%"=="6" goto run_tests
if "%choice%"=="7" goto open_dashboard
if "%choice%"=="8" goto view_reports
if "%choice%"=="9" goto open_dooray
if /i "%choice%"=="A" goto system_reset
if /i "%choice%"=="B" goto create_backup
if /i "%choice%"=="C" goto edit_config
if "%choice%"=="0" goto exit
goto invalid_choice

:start_watchhamster
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🚀 워치햄스터 시작 중...                                 ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "🚀POSCO_워치햄스터_시작.bat"
goto return_to_menu

:stop_monitoring
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🛑 모니터링 시스템 중지 중...                           ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "🛑POSCO_모니터링_중지.bat"
goto return_to_menu

:check_status
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📊 시스템 상태 확인 중...                               ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "📊POSCO_상태_확인.bat"
goto return_to_menu

:git_update
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🔄 Git 업데이트 실행 중...                              ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "🔄POSCO_Git_업데이트.bat"
goto return_to_menu

:check_logs
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📋 로그 파일 확인 중...                                 ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "📋POSCO_로그_확인.bat"
goto return_to_menu

:run_tests
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🧪 테스트 실행 중...                                    ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
call "🧪POSCO_테스트_실행.bat"
goto return_to_menu

:open_dashboard
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🌐 대시보드 열기                                        ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🌐 GitHub Pages 대시보드를 브라우저에서 열고 있습니다...
echo 🔗 URL: https://shuserker.github.io/infomax_api/
echo.
start https://shuserker.github.io/infomax_api/
echo ✅ 대시보드가 브라우저에서 열렸습니다.
echo.
pause
goto return_to_menu

:view_reports
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📈 통합 리포트 보기                                     ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📊 통합 분석 리포트를 브라우저에서 열고 있습니다...
echo 🔗 URL: https://shuserker.github.io/infomax_api/reports/
echo.
start https://shuserker.github.io/infomax_api/reports/
echo ✅ 리포트가 브라우저에서 열렸습니다.
echo.
pause
goto return_to_menu

:open_dooray
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📱 Dooray 채널 열기                                     ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📱 Dooray 메신저를 브라우저에서 열고 있습니다...
echo 🔗 POSCO 뉴스 알림 채널을 확인하세요.
echo.
start https://dooray.com/
echo ✅ Dooray가 브라우저에서 열렸습니다.
echo 💡 POSCO 뉴스 채널에서 최신 알림을 확인하세요.
echo.
pause
goto return_to_menu

:system_reset
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🔧 시스템 리셋                                          ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo ⚠️ 경고: 시스템 전체를 초기화합니다.
echo 📋 다음 작업이 수행됩니다:
echo    • 모든 모니터링 프로세스 중지
echo    • 로그 파일 정리
echo    • 상태 파일 초기화
echo    • 메타데이터 리셋
echo.
set /p confirm=🤔 정말로 시스템을 리셋하시겠습니까? (Y/N): 
if /i "%confirm%"=="Y" (
    echo.
    echo 🔄 시스템 리셋 실행 중...
    python posco_report_system_reset.py
    echo ✅ 시스템 리셋 완료!
) else (
    echo ❌ 시스템 리셋이 취소되었습니다.
)
echo.
pause
goto return_to_menu

:create_backup
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    📦 백업 생성                                            ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📦 현재 시스템 상태를 백업하고 있습니다...
echo.
set backup_name=POSCO_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%
echo 📁 백업 이름: %backup_name%
echo.
mkdir "backups\%backup_name%" 2>nul
copy "*.json" "backups\%backup_name%\" >nul 2>&1
copy "*.log" "backups\%backup_name%\" >nul 2>&1
copy "config.py" "backups\%backup_name%\" >nul 2>&1
echo ✅ 백업이 완료되었습니다!
echo 📂 백업 위치: backups\%backup_name%\
echo.
pause
goto return_to_menu

:edit_config
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██    🛠️ 설정 편집                                            ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🛠️ 편집할 설정 파일을 선택하세요:
echo.
echo 1. config.py - 메인 설정 파일
echo 2. system_status.json - 시스템 상태 파일
echo 3. 취소
echo.
set /p config_choice=선택 (1-3): 
if "%config_choice%"=="1" (
    echo 📝 config.py 파일을 메모장에서 열고 있습니다...
    notepad config.py
) else if "%config_choice%"=="2" (
    echo 📝 system_status.json 파일을 메모장에서 열고 있습니다...
    notepad system_status.json
) else (
    echo ❌ 취소되었습니다.
)
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
echo ═══════════════════════════════════════════════════════════════════════════════
echo                            🎯 작업 완료                                      
echo ═══════════════════════════════════════════════════════════════════════════════
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
echo ██    👋 POSCO 모니터링 관리 센터를 종료합니다                ██
echo ██                                                            ██
echo ██    🔙 워치햄스터 총괄 센터로 돌아가세요!                   ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 📱 문제가 있으면 관리자에게 문의하세요.
echo 🔗 대시보드: https://shuserker.github.io/infomax_api/
echo.
pause
exit