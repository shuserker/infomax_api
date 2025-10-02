@echo off
REM WatchHamster 윈도우 실행 스크립트
REM 더블클릭으로 바로 실행 가능!

echo 🐹 WatchHamster 윈도우 실행기
echo ================================

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    echo 📥 Python 설치: https://python.org
    pause
    exit /b 1
)

echo ✅ Python 설치됨

REM tkinter 확인
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ tkinter 문제 감지 - 백엔드 모드로 실행
    echo 🔄 GUI 없이 모든 기능 제공
    python run_without_gui.py
) else (
    echo ✅ tkinter 정상 - GUI 모드로 실행
    echo 🖥️ GUI 창이 열립니다...
    python main_gui.py
)

echo.
echo 🎊 WatchHamster 실행 완료!
pause