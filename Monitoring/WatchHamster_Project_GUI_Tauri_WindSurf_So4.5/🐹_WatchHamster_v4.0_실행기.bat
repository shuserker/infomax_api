@echo off
chcp 65001 >nul
title WatchHamster v4.0 통합 모니터링 시스템

REM 🐹 WatchHamster v4.0 통합 모니터링 시스템 원클릭 실행기
REM ===========================================================

echo.
echo ================================================================
echo 🐹 WatchHamster v4.0 통합 모니터링 시스템 완전체
echo ================================================================
echo 📈 POSCO 뉴스 모니터링 시스템
echo 📊 InfoMax API 테스트 플랫폼 (58개+ API 지원)
echo 🤖 28개 자동갱신 로직 & 스마트 스케줄링
echo 🌐 웹훅 통합 & 실시간 알림 시스템
echo ⚙️  백업, 수리, 품질관리 자동화 도구
echo ================================================================
echo.

REM 현재 디렉토리 확인
echo 📍 WatchHamster 본부: %CD%
echo.

REM Node.js 설치 확인
echo 🔍 시스템 환경 체크 중...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js가 설치되지 않았습니다!
    echo    https://nodejs.org 에서 설치해주세요.
    pause
    exit /b 1
) else (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js: %NODE_VERSION%
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm이 설치되지 않았습니다!
    pause
    exit /b 1
) else (
    for /f %%i in ('npm --version') do set NPM_VERSION=%%i
    echo ✅ npm: v%NPM_VERSION%
)

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python이 설치되지 않았습니다 (백엔드 기능 제한)
) else (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ Python: %PYTHON_VERSION%
)

REM package.json 존재 확인
if not exist "package.json" (
    echo ❌ package.json을 찾을 수 없습니다!
    echo    올바른 WatchHamster 프로젝트 디렉토리에서 실행하세요.
    pause
    exit /b 1
)

echo ✅ WatchHamster 시스템 구조 정상
echo.

REM 사용자 선택 메뉴
:MENU
echo 🎯 WatchHamster v4.0 실행 옵션:
echo [1] 🚀 WatchHamster 풀스택 실행 (의존성 자동 설치 + 전체 시스템 시작)
echo [2] 📦 의존성만 설치
echo [3] 🌐 프론트엔드만 시작 (InfoMax API 테스트 플랫폼)
echo [4] 🐍 백엔드만 시작 (웹훅 & 모니터링 서비스)
echo [5] 🏗️  빌드 및 프로덕션 프리뷰
echo [6] 🧹 시스템 초기화 (캐시 정리 + 재설치)
echo [7] 📋 WatchHamster 시스템 상태 체크
echo [8] ❌ 종료
echo.
set /p choice=선택 (1-8): 

if "%choice%"=="1" goto FULL_STACK
if "%choice%"=="2" goto INSTALL_ONLY
if "%choice%"=="3" goto FRONTEND_ONLY
if "%choice%"=="4" goto BACKEND_ONLY
if "%choice%"=="5" goto BUILD_PREVIEW
if "%choice%"=="6" goto SYSTEM_RESET
if "%choice%"=="7" goto SYSTEM_STATUS
if "%choice%"=="8" goto EXIT
echo ❌ 잘못된 선택입니다. 1-8 사이의 숫자를 입력하세요.
goto MENU

:FULL_STACK
echo 🚀 WatchHamster v4.0 풀스택 실행 모드
echo.
echo 📦 의존성 설치 중...
call npm install
if errorlevel 1 (
    echo ❌ 의존성 설치 실패!
    pause
    exit /b 1
)
echo ✅ 의존성 설치 완료!
echo.
echo 🌐 WatchHamster 통합 시스템 시작 중...
echo ================================================================
echo 🐹 WatchHamster v4.0 Control Center
echo 📈 POSCO 뉴스 모니터링: 활성화
echo 📊 InfoMax API 플랫폼: http://localhost:1420/api-packages
echo 🤖 자동갱신 시스템: 백그라운드 실행
echo 🌐 웹훅 통합: 준비완료
echo ================================================================
echo 🎯 주요 기능:
echo   • API 테스트: 58개+ 금융 API 완전 지원
echo   • 자동갱신: 28개 스마트 로직 & 스케줄링
echo   • 실시간 모니터링: POSCO 뉴스 변경사항 추적
echo   • 웹훅 알림: Dooray 통합 실시간 알림
echo ================================================================
echo 시스템 종료: Ctrl+C
echo.
call npm run dev
goto END

:INSTALL_ONLY
echo 📦 WatchHamster 의존성 설치 중...
call npm install
if errorlevel 1 (
    echo ❌ 의존성 설치 실패!
    pause
    exit /b 1
)
echo ✅ 의존성 설치 완료!
echo 💡 이제 'npm run dev' 명령으로 WatchHamster를 시작할 수 있습니다.
goto END

:FRONTEND_ONLY
echo 🌐 WatchHamster 프론트엔드 시작 중...
echo ================================================================
echo 📍 InfoMax API 테스트 플랫폼: http://localhost:1420/api-packages
echo 🐹 WatchHamster v4.0 - API 테스트 모듈
echo ================================================================
echo 시스템 종료: Ctrl+C
echo.
call npm run dev
goto END

:BACKEND_ONLY
echo 🐍 WatchHamster 백엔드 서비스 시작 중...

if exist "python-backend" (
    cd python-backend
    if exist "requirements.txt" (
        echo Python 의존성 설치 중...
        python -m pip install -r requirements.txt
    )
    
    echo ================================================================
    echo 🐹 WatchHamster 백엔드 서비스 활성화
    echo 📈 POSCO 뉴스 모니터링 활성화
    echo 🌐 웹훅 서비스 대기 중
    echo ================================================================
    
    python -m api.webhook_manager
) else (
    echo ⚠️  백엔드 디렉토리를 찾을 수 없습니다.
    echo 프론트엔드만 실행합니다...
    call npm run dev
)
goto END

:BUILD_PREVIEW
echo 🏗️  WatchHamster 시스템 빌드 중...
call npm run build
if errorlevel 1 (
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)
echo ✅ 빌드 완료!
echo.
echo 🎭 프로덕션 프리뷰 서버 시작 중...
call npm run preview
goto END

:SYSTEM_RESET
echo 🧹 WatchHamster 시스템 초기화 중...

if exist "node_modules" (
    rmdir /s /q "node_modules"
    echo ✅ node_modules 정리 완료
)

if exist "package-lock.json" (
    del "package-lock.json"
    echo ✅ package-lock.json 정리 완료
)

call npm cache clean --force
echo ✅ npm 캐시 정리 완료

echo.
echo 📦 WatchHamster 시스템 재설치 중...
call npm install
if errorlevel 1 (
    echo ❌ 재설치 실패!
    pause
    exit /b 1
)
echo ✅ 시스템 초기화 완료!
echo.
set /p start_server=🐹 WatchHamster를 시작하시겠습니까? (y/n): 
if /i "%start_server%"=="y" call npm run dev
goto END

:SYSTEM_STATUS
echo 📋 WatchHamster v4.0 시스템 상태 체크
echo ================================================================

echo 📁 프로젝트 구조:
if exist "package.json" (echo ✅ package.json) else (echo ❌ package.json)
if exist "src" (echo ✅ src/ ^(프론트엔드^)) else (echo ❌ src/)
if exist "python-backend" (echo ✅ python-backend/ ^(백엔드^)) else (echo ⚠️  python-backend/)
if exist "core" (echo ✅ core/ ^(모니터링^)) else (echo ⚠️  core/)

echo.
echo 🔧 핵심 모듈:
if exist "src\pages\ApiPackageManagement.tsx" (echo ✅ InfoMax API 테스트 모듈) else (echo ❌ API 테스트 모듈)
if exist "src\utils\parameterDefaultManager.ts" (echo ✅ 자동갱신 시스템) else (echo ❌ 자동갱신 시스템)
if exist "src\utils\apiCrawlingMapper.ts" (echo ✅ API 크롤링 매핑) else (echo ❌ 크롤링 매핑)

echo.
echo 📊 통계:
echo • 지원 API: 58개+
echo • 자동갱신 로직: 28개

echo ================================================================
pause
goto MENU

:EXIT
echo 👋 WatchHamster를 종료합니다.
exit /b 0

:END
echo.
echo 🎉 WatchHamster v4.0 작업 완료!
echo 🐹 최고의 모니터링 시스템과 함께하세요!
echo ================================================================
pause
