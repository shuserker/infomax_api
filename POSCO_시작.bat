@echo off
REM ============================================================================
REM Posco 시작
REM POSCO 시스템 구성요소
REM 
REM WatchHamster v3.0 및 POSCO News 250808 호환
REM Created: 2025-08-08
REM ============================================================================

title POSCO 제어 센터
powershell.exe -ExecutionPolicy Bypass -File "%~dp0posco_control_center.ps1"
pause