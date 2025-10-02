@echo off
REM ============================================================================
REM Posco 로그 확인
REM POSCO 시스템 구성요소
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

chcp 65001 > nul
title POSCO 로그 확인 📋

echo.
echo ========================================
echo    📋 POSCO 시스템 로그 확인 📄
echo ========================================
echo.

cd /d "%~dp0"

echo 📄 워치햄스터 로그 (WatchHamster.log):
echo ========================================
if exist ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log" (
    echo 📅 파일 정보:
    for %%A in (".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log") do (
        echo    크기: %%~zA bytes
        echo    수정일: %%~tA
    )
    echo.
    echo 📋 최근 50줄:
    echo ----------------------------------------
    powershell "Get-Content '.naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log' -Tail 50 -Encoding UTF8"
) else (
    echo ❌ WatchHamster.log 파일이 없습니다.
)

echo.
echo.
echo 📊 시스템 상태 (system_status.json):
echo ========================================
if exist ".naming_backup/config_data_backup/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/backup_archive_20250806/.naming_backup/config_data_backup/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/backup_archive_20250806/system_status.json" (
    type system_status.json
) else (
    echo ❌ system_status.json 파일이 없습니다.
)

echo.
echo.
echo 📁 실시간 모니터 상태 (realtime_monitor_state.json):
echo ========================================
# BROKEN_REF: if exist "realtime_monitor_state.json" (
    type realtime_monitor_state.json
) else (
    echo ❌ realtime_monitor_state.json 파일이 없습니다.
)

echo.
echo.
echo 📊 최근 생성된 리포트 파일들:
echo ========================================
if exist "reports\" (
    echo 📁 reports 디렉토리:
    dir reports\*.html /o-d /b 2>nul | head -5
) else (
    echo ❌ reports 디렉토리가 없습니다.
)

echo.
echo.
echo 🔍 현재 실행 중인 프로세스:
echo ========================================
tasklist | findstr python.exe

echo.
echo 📋 로그 확인 완료!
echo.
pause