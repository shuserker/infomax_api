@echo off
echo ========================================
echo POSCO 뉴스 모니터 환경 설정
echo ========================================

echo Python 버전 확인 중...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    echo Python 3.x를 설치하고 PATH에 추가해주세요.
    pause
    exit /b 1
)

echo.
echo pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 필수 라이브러리 설치 중...
pip install -r requirements.txt

echo.
echo 연결 테스트 중...
python run_monitor.py 6

echo.
echo ========================================
echo 환경 설정이 완료되었습니다!
echo ========================================
echo.
echo 다음 단계:
echo 1. config.py에서 웹훅 URL 확인
echo 2. start_posco_monitor.bat으로 백그라운드 실행
echo 3. view_monitor_log.bat으로 로그 확인
echo.
pause