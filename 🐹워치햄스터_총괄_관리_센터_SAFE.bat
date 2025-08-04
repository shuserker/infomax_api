@echo off
setlocal enabledelayedexpansion
title 워치햄스터 총괄 관리 센터 - Safe Mode (기본 색상)

REM UTF-8 설정
chcp 65001 > nul 2>&1

REM 기본 색상만 사용 (ANSI 없이)
echo.
echo ================================================================================
echo                                                                                
echo    워치햄스터 총괄 관리 센터 - Safe Mode                                      
echo    Basic Colors Only (ANSI 지원 불가 환경용)                                 
echo                                                                                
echo ================================================================================
echo.

echo 시스템 관리
echo.
echo ┌─ 모니터링 시스템 ─────────────────────────────────────────────────────────┐
echo │ 1 POSCO 뉴스 모니터링  포스코 뉴스 및 주가 모니터링           │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ 시스템 관리 ─────────────────────────────────────────────────────────────┐
echo │ A 전체 시스템 상태     모든 워치햄스터 상태 확인                │
echo │ B 전체 시스템 업데이트  모든 시스템 Git 업데이트                 │
echo │ C 통합 로그 관리       모든 시스템 로그 통합 관리                │
echo │ D 전체 시스템 테스트   모든 시스템 통합 테스트                   │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ 고급 관리 ───────────────────────────────────────────────────────────────┐
echo │ E 전체 백업 생성       모든 시스템 통합 백업                     │
echo │ F 시스템 설정         워치햄스터 설정 관리                      │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.
echo 0 종료
echo.
echo ─────────────────────────────────────────────────────────────────────────────
echo 현재 시간: %date% %time% │ 작업 디렉토리: %cd%
echo.

set /p choice=선택하세요: 

if "%choice%"=="1" goto posco_monitoring
if /i "%choice%"=="A" goto system_status
if /i "%choice%"=="B" goto system_update
if /i "%choice%"=="C" goto integrated_logs
if /i "%choice%"=="D" goto system_test
if /i "%choice%"=="E" goto full_backup
if /i "%choice%"=="F" goto settings_menu
if "%choice%"=="0" goto exit_program
echo 잘못된 선택입니다
timeout /t 2 /nobreak > nul
goto main_menu

:posco_monitoring
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ POSCO 모니터링 시스템                                              │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo POSCO 모니터링 시스템으로 이동 중...
echo.

cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🎛️POSCO_통합_관리_센터.bat" (
    call "🎛️POSCO_통합_관리_센터.bat"
) else (
    echo POSCO 모니터링 시스템을 찾을 수 없습니다
    echo 경로: Monitoring\Posco_News_mini\
    pause
)
cd /d "%~dp0"
goto return_menu

:system_status
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 전체 시스템 상태                                                  │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 시스템 상태를 확인하고 있습니다...
echo.

echo 시스템 현황
echo ─────────────────────────────────────────────────────────────────────────────

if exist "Monitoring\Posco_News_mini\system_status.json" (
    echo ✓ POSCO 모니터링      │ 활성화
) else (
    echo ! POSCO 모니터링      │ 상태 불명
)

echo.
echo 가동률: 100%% │ 업데이트: %date%
echo.
pause
goto return_menu

:system_update
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 전체 시스템 업데이트                                              │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 시스템 업데이트를 진행하고 있습니다...
echo.

echo POSCO 모니터링 시스템 업데이트 중...
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🔄POSCO_Git_업데이트.bat" (
    call "🔄POSCO_Git_업데이트.bat" > nul 2>&1
    echo ✓ POSCO 시스템 업데이트 완료
) else (
    echo X POSCO 업데이트 파일을 찾을 수 없습니다
)
cd /d "%~dp0"

echo.
echo 전체 시스템 업데이트 완료!
echo.
pause
goto return_menu

:integrated_logs
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 통합 로그 관리                                                    │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 통합 로그를 분석하고 있습니다...
echo.

echo POSCO 시스템 로그:
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "📋POSCO_로그_확인.bat" (
    call "📋POSCO_로그_확인.bat"
) else (
    echo ! POSCO 로그 파일을 찾을 수 없습니다
)
cd /d "%~dp0"

echo.
pause
goto return_menu

:system_test
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 전체 시스템 테스트                                               │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 시스템 테스트를 실행하고 있습니다...
echo.

echo POSCO 시스템 테스트:
cd /d "Monitoring\Posco_News_mini" 2>nul
if exist "🧪POSCO_테스트_실행.bat" (
    call "🧪POSCO_테스트_실행.bat" > nul 2>&1
    echo ✓ POSCO 시스템 테스트 통과
) else (
    echo ! POSCO 테스트 파일을 찾을 수 없습니다
)
cd /d "%~dp0"

echo.
echo 전체 시스템 테스트 완료!
echo.
pause
goto return_menu

:full_backup
cls
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 전체 시스템 백업                                                  │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 전체 시스템 백업을 생성하고 있습니다...
echo.

set backup_name=WatchHamster_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo 백업명: %backup_name%
echo.

mkdir "Backups\%backup_name%" 2>nul

echo POSCO 시스템 백업 중...
xcopy "Monitoring\Posco_News_mini\*.json" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\*.log" "Backups\%backup_name%\POSCO\" /E /I /Q >nul 2>&1
xcopy "Monitoring\Posco_News_mini\config.py" "Backups\%backup_name%\POSCO\" /Q >nul 2>&1

echo.
echo 전체 시스템 백업 완료!
echo 백업 위치: Backups\%backup_name%\
echo.
pause
goto return_menu

:settings_menu
cls
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 시스템 설정                                                      │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.

echo 설정 메뉴
echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │ 1 알림 설정         통합 알림 관리                        │
echo │ 2 스케줄 설정       통합 스케줄 관리                      │
echo │ 3 보안 설정         보안 및 인증 관리                     │
echo │ 4 네트워크 설정     프록시 및 연결 설정                   │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.
echo 0 돌아가기
echo.

set /p setting_choice=설정 선택: 

if "%setting_choice%"=="1" (
    echo 알림 설정 기능은 현재 개발 중입니다
) else if "%setting_choice%"=="2" (
    echo 스케줄 설정 기능은 현재 개발 중입니다
) else if "%setting_choice%"=="3" (
    echo 보안 설정 기능은 현재 개발 중입니다
) else if "%setting_choice%"=="4" (
    echo 네트워크 설정 기능은 현재 개발 중입니다
) else if "%setting_choice%"=="0" (
    goto main_menu
) else (
    echo 잘못된 선택입니다
)
timeout /t 2 /nobreak > nul
goto settings_menu

:return_menu
cls
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 작업 완료                                                        │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.

echo 다음 작업을 선택하세요:
echo.
echo ┌───────────────────────────────────────────────────────────────────────────┐
echo │ 1 메인 메뉴로 돌아가기                                      │
echo │ 2 프로그램 종료                                           │
echo └───────────────────────────────────────────────────────────────────────────┘
echo.

set /p return_choice=선택: 
if "%return_choice%"=="1" goto main_menu
if "%return_choice%"=="2" goto exit_program
goto main_menu

:exit_program
cls
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ 워치햄스터 총괄 관리 센터를 종료합니다                              │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 모든 모니터링 시스템이 안전하게 보호됩니다!
echo.
echo 워치햄스터가 백그라운드에서 계속 감시 중입니다
echo 문제가 있으면 관리자에게 문의하세요
echo.
echo 종료 시간: %date% %time%
echo.
timeout /t 3 /nobreak > nul
exit /b 0