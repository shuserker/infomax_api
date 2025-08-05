@echo off
title POSCO 제어 센터
powershell.exe -ExecutionPolicy Bypass -File "%~dp0posco_control_center.ps1"
pause