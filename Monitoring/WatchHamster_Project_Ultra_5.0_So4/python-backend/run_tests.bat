@echo off
echo 🚀 WatchHamster 백엔드 단위 테스트 실행
echo ============================================================

cd /d "%~dp0"

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 의존성 설치 확인
echo 테스트 의존성 설치 확인 중...
python -m pip install -r requirements.txt --quiet

REM 테스트 실행
echo.
echo 테스트 실행 중...
python run_tests.py %*

echo.
echo 테스트 완료!
pause