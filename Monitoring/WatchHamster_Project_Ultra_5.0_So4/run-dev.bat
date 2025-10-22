@echo off
chcp 65001 >nul
title WatchHamster Dev Server

echo.
echo ===============================================================
echo                  WatchHamster Starting                        
echo                                                              
echo   Please wait... Starting servers!              
echo ===============================================================
echo.

:: Clean previous processes
echo [CLEAN] Cleaning previous processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

:: Check Node.js
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js not installed!
    echo         Run setup.bat first.
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not installed!
    echo         Run setup.bat first.
    pause
    exit /b 1
)

:: Check node_modules
if not exist "node_modules" (
    echo [ERROR] Packages not installed!
    echo         Run setup.bat first.
    pause
    exit /b 1
)

echo [OK] Environment check complete!
echo.

echo [START] Starting WatchHamster dev server...
echo.
echo ---------------------------------------------------------------
echo   Tips:                                                      
echo   - Browser will open automatically                               
echo   - Press Ctrl+C in this window to stop                    
echo   - Check messages in this window if problems occur                  
echo ---------------------------------------------------------------
echo.

:: Start dev server
echo [START] Starting server... (may take up to 30 seconds)
echo.

call npm run dev

:: Handle errors
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Server start failed!
    echo.
    echo [FIX] Solutions:
    echo 1. Run setup.bat again
    echo 2. Restart computer
    echo 3. Check if ports 8000, 1420 are used by other programs
    echo.
    pause
)