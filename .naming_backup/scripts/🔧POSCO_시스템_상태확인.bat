@echo off
chcp 65001 > nul
title POSCO 시스템 상태 확인 🔍

echo.
echo ========================================
echo    🔍 POSCO 시스템 상태 확인 📊
echo ========================================
echo.

cd /d "%~dp0"

echo 🐹 WatchHamster v3.0 상태:
tasklist | findstr python.exe | findstr monitor_WatchHamster
if errorlevel 1 (
    echo    ❌ 워치햄스터가 실행되지 않음
) else (
    echo    ✅ 워치햄스터 실행 중
)

echo.
echo 📰 실시간 뉴스 모니터 상태:
tasklist | findstr python.exe | findstr realtime_news_monitor
if errorlevel 1 (
    echo    ❌ 실시간 뉴스 모니터가 실행되지 않음
) else (
    echo    ✅ 실시간 뉴스 모니터 실행 중
)

echo.
echo 📊 통합 리포트 스케줄러 상태:
tasklist | findstr python.exe | findstr integrated_report_scheduler
if errorlevel 1 (
    echo    ❌ 통합 리포트 스케줄러가 실행되지 않음
) else (
    echo    ✅ 통합 리포트 스케줄러 실행 중
)

echo.
echo 🔍 전체 Python 프로세스:
tasklist | findstr python.exe

echo.
echo 📁 최근 로그 파일:
if exist ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log" (
    echo    📄 WatchHamster.log (크기: 
    for %%A in (".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log") do echo %%~zA bytes)
    echo    📅 마지막 수정: 
    for %%A in (".naming_backup/config_data_backup/Monitoring/Posco_News_mini/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log") do echo %%~tA
) else (
    echo    ❌ WatchHamster.log 파일 없음
)

echo.
echo 📊 시스템 상태 파일:
if exist ".naming_backup/config_data_backup/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/backup_archive_20250806/.naming_backup/config_data_backup/.naming_backup/config_data_backup/Monitoring/Posco_News_mini/backup_archive_20250806/system_status.json" (
    echo    📄 system_status.json 존재
    type system_status.json 2>nul
) else (
    echo    ❌ system_status.json 파일 없음
)

echo.
echo 🌐 GitHub Pages 상태:
echo    🔗 대시보드: https://shuserker.github.io/infomax_api/
echo    📊 리포트: https://shuserker.github.io/infomax_api/reports/

echo.
pause