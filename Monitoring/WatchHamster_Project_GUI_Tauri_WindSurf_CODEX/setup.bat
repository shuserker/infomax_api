@echo off
chcp 65001 >nul
title WatchHamster Setup

echo.
echo ===============================================================
echo                   WatchHamster Setup
echo                                                              
echo   This script will install everything automatically!              
echo ===============================================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with admin rights.
) else (
    echo [WARN] Admin rights may be needed.
    echo       Try "Run as administrator" if problems occur.
)
echo.

:: Check Node.js
echo [CHECK] Checking Node.js...
node --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo [OK] Node.js installed: %NODE_VERSION%
) else (
    echo [ERROR] Node.js not installed!
    echo         Download from https://nodejs.org
    pause
    exit /b 1
)

:: Check Python
echo [CHECK] Checking Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] Python installed: %PYTHON_VERSION%
) else (
    echo [ERROR] Python not installed!
    echo         Download from https://python.org
    pause
    exit /b 1
)

echo.
echo [INSTALL] Starting package installation...
echo           (First install may take 2-3 minutes)
echo.

:: Install Node.js packages
echo [INSTALL] Installing Node.js packages...
call npm install
if %errorLevel% neq 0 (
    echo [ERROR] Node.js package installation failed!
    echo         Check internet connection and try again.
    pause
    exit /b 1
)
echo [OK] Node.js packages installed!

:: Install Python packages
echo [INSTALL] Installing Python packages...
cd python-backend
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Python package installation failed!
    echo         Try: python -m pip install --upgrade pip
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Python packages installed!

:: Test backend
echo [TEST] Testing backend...
cd python-backend
python test_backend.py >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Backend test passed!
) else (
    echo [WARN] Backend test warnings, but continuing...
)
cd ..

echo.
echo ===============================================================
echo                   Setup Complete!                             
echo                                                              
echo   Now run run-dev.bat to start WatchHamster!  
echo                                                              
echo   Or run 'npm run dev' in terminal.           
echo ===============================================================
echo.

echo Access URL after running: http://localhost:1420
echo Usage guide: QUICK_START.md
echo.

pause