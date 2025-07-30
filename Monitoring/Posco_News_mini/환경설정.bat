@echo off
chcp 65001 > nul
title POSCO 미니뉴스 - 환경설정
color 0E

echo.
echo ========================================
echo   🔧 POSCO 미니뉴스 환경설정
echo ========================================
echo.

cd /d "%~dp0"

echo 🐍 Python 버전 확인 중...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    echo Python 3.x를 설치하고 PATH에 추가해주세요.
    pause
    exit /b 1
)

echo.
echo 📦 pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 📚 필수 라이브러리 설치 중...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 라이브러리 설치 실패
        pause
        exit /b 1
    )
    echo ✅ 라이브러리 설치 완료
) else (
    echo ⚠️ requirements.txt 파일이 없습니다.
)

echo.
echo 🧪 연결 테스트 중...
python run_monitor.py 6

echo.
echo ========================================
echo   🎉 환경 설정이 완료되었습니다!
echo ========================================
echo.
echo 📋 다음 단계:
echo 1. config.py에서 웹훅 URL 확인
echo 2. 🛡️ 24시간 모니터링: POSCO_워치햄스터_시작.bat
echo 3. 🚀 일회성 작업: 🚀일회성작업_실행.bat
echo 4. 📊 로그 확인: POSCO_미니뉴스_스마트모니터링_로그확인.bat
echo.
pause