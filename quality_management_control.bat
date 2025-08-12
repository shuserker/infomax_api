@echo off
REM POSCO 시스템 지속적 품질 관리 제어 스크립트 (Windows)
REM Quality Management Control Script for Windows

setlocal enabledelayedexpansion

REM 색상 코드 (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 헤더 출력
echo ==================================================================
echo 🎯 POSCO 시스템 지속적 품질 관리 제어 센터
echo    Continuous Quality Management Control Center
echo ==================================================================
echo.

REM 명령어 파싱
if "%1"=="" goto :show_help
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="start-monitor" goto :start_monitoring
if "%1"=="run-pipeline" goto :run_pipeline
if "%1"=="generate-dashboard" goto :generate_dashboard
if "%1"=="generate-report" goto :generate_report
if "%1"=="run-tests" goto :run_tests
if "%1"=="status" goto :check_status
if "%1"=="install-deps" goto :install_dependencies

echo %RED%[ERROR]%NC% 알 수 없는 명령어: %1
echo.
goto :show_help

:show_help
echo 사용법: %0 [COMMAND] [OPTIONS]
echo.
echo 명령어:
echo   start-monitor [DURATION]  - 지속적 모니터링 시작 (기본: 3600초)
echo   run-pipeline             - CI/CD 파이프라인 실행
echo   generate-dashboard       - 품질 대시보드 생성
echo   generate-report          - 품질 보고서 생성
echo   run-tests               - 품질 관리 시스템 테스트 실행
echo   status                  - 현재 시스템 상태 확인
echo   install-deps            - 필요한 의존성 설치
echo   help                    - 이 도움말 표시
echo.
echo 예시:
echo   %0 start-monitor 1800    # 30분간 모니터링
echo   %0 run-pipeline          # 파이프라인 실행
echo   %0 generate-dashboard    # 대시보드 생성
echo.
goto :end

:check_dependencies
echo %BLUE%[INFO]%NC% 의존성 확인 중...

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python이 설치되어 있지 않습니다.
    exit /b 1
)

REM 필수 패키지 확인
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% psutil 패키지가 누락되었습니다.
    echo %BLUE%[INFO]%NC% 다음 명령으로 설치하세요: %0 install-deps
    exit /b 1
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% pyyaml 패키지가 누락되었습니다.
    echo %BLUE%[INFO]%NC% 다음 명령으로 설치하세요: %0 install-deps
    exit /b 1
)

python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% schedule 패키지가 누락되었습니다.
    echo %BLUE%[INFO]%NC% 다음 명령으로 설치하세요: %0 install-deps
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% 모든 의존성이 설치되어 있습니다.
exit /b 0

:install_dependencies
echo %BLUE%[INFO]%NC% 필요한 의존성 설치 중...

REM pip 업그레이드
python -m pip install --upgrade pip

REM 필수 패키지 설치
python -m pip install psutil pyyaml schedule

echo %GREEN%[SUCCESS]%NC% 의존성 설치 완료
goto :end

:start_monitoring
set duration=%2
if "%duration%"=="" set duration=3600

echo %BLUE%[INFO]%NC% 지속적 모니터링 시작 (지속 시간: %duration%초)

call :check_dependencies
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 의존성 확인 실패
    goto :end
)

python start_quality_management.py --mode monitor --duration %duration% --verbose
goto :end

:run_pipeline
echo %BLUE%[INFO]%NC% CI/CD 파이프라인 실행

call :check_dependencies
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 의존성 확인 실패
    goto :end
)

python start_quality_management.py --mode pipeline --verbose
goto :end

:generate_dashboard
echo %BLUE%[INFO]%NC% 품질 대시보드 생성

call :check_dependencies
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 의존성 확인 실패
    goto :end
)

python start_quality_management.py --mode dashboard --verbose
goto :end

:generate_report
echo %BLUE%[INFO]%NC% 품질 보고서 생성

call :check_dependencies
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 의존성 확인 실패
    goto :end
)

python start_quality_management.py --mode report --verbose
goto :end

:run_tests
echo %BLUE%[INFO]%NC% 품질 관리 시스템 테스트 실행

call :check_dependencies
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 의존성 확인 실패
    goto :end
)

if exist "test_continuous_quality_management.py" (
    python test_continuous_quality_management.py
) else (
    echo %RED%[ERROR]%NC% 테스트 파일을 찾을 수 없습니다: test_continuous_quality_management.py
)
goto :end

:check_status
echo %BLUE%[INFO]%NC% 시스템 상태 확인

echo 📊 시스템 리소스:
for /f %%i in ('python -c "import psutil; print(f'{psutil.cpu_percent(interval=1):.1f}%%')"') do echo   - CPU 사용률: %%i
for /f %%i in ('python -c "import psutil; print(f'{psutil.virtual_memory().percent:.1f}%%')"') do echo   - 메모리 사용률: %%i
for /f %%i in ('python -c "import psutil; print(f'{psutil.disk_usage(\".\").percent:.1f}%%')"') do echo   - 디스크 사용률: %%i

echo.
echo 📁 중요 파일 존재 여부:
if exist "continuous_quality_management_system.py" (
    echo   ✅ continuous_quality_management_system.py
) else (
    echo   ❌ continuous_quality_management_system.py (누락)
)

if exist "start_quality_management.py" (
    echo   ✅ start_quality_management.py
) else (
    echo   ❌ start_quality_management.py (누락)
)

if exist "ci_config.yaml" (
    echo   ✅ ci_config.yaml
) else (
    echo   ❌ ci_config.yaml (누락)
)

if exist "test_continuous_quality_management.py" (
    echo   ✅ test_continuous_quality_management.py
) else (
    echo   ❌ test_continuous_quality_management.py (누락)
)

echo.
echo 🐍 Python 환경:
for /f %%i in ('python --version') do echo   - Python 버전: %%i
echo   - 현재 디렉토리: %CD%

REM 최근 로그 파일 확인
if exist "quality_management.log" (
    echo.
    echo 📋 최근 로그 (마지막 10줄):
    powershell "Get-Content quality_management.log -Tail 10"
)

goto :end

:end
pause