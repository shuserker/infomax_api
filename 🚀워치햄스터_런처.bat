@echo off
chcp 65001 > nul 2>&1
title 워치햄스터 런처 - 버전 선택

echo.
echo ================================================================================
echo                                                                                
echo    워치햄스터 런처 - 사용할 버전을 선택하세요                                 
echo                                                                                
echo ================================================================================
echo.
echo 사용 가능한 버전:
echo.
echo 1. v4.0 풀 버전 (고급 사용자)
echo    - 모든 기능 포함
echo    - Windows 11 Fluent Design
echo    - 고급 설정 및 테마 변경
echo    - RGB 색상 지원 필요
echo.
echo 2. MODERN 버전 (일반 사용자)
echo    - 핵심 기능만 포함
echo    - 간단하고 직관적
echo    - 빠른 실행 속도
echo    - RGB 색상 지원 필요
echo.
echo 3. SAFE 버전 (호환성 우선)
echo    - 기본 색상만 사용
echo    - 모든 터미널에서 작동
echo    - ANSI 지원 불필요
echo    - 안정성 최우선
echo.
echo 4. 기존 버전 (레거시)
echo    - 기존 사용자용
echo    - 기본 ANSI 색상
echo    - 호환성 보장
echo.
echo ================================================================================
echo.

:select_version
set /p choice=사용할 버전을 선택하세요 (1-4): 

if "%choice%"=="1" (
    echo.
    echo v4.0 풀 버전을 시작합니다...
    echo Windows 11 Fluent Design 적용 중...
    timeout /t 2 /nobreak > nul
    call "🐹워치햄스터_총괄_관리_센터_v4.bat"
) else if "%choice%"=="2" (
    echo.
    echo MODERN 버전을 시작합니다...
    echo 간단하고 현대적인 인터페이스 로딩 중...
    timeout /t 2 /nobreak > nul
    call "🐹워치햄스터_총괄_관리_센터_MODERN.bat"
) else if "%choice%"=="3" (
    echo.
    echo SAFE 버전을 시작합니다...
    echo 호환성 우선 모드로 실행 중...
    timeout /t 2 /nobreak > nul
    call "🐹워치햄스터_총괄_관리_센터_SAFE.bat"
) else if "%choice%"=="4" (
    echo.
    echo 기존 버전을 시작합니다...
    echo 레거시 모드로 실행 중...
    timeout /t 2 /nobreak > nul
    call "🐹워치햄스터_총괄_관리_센터.bat"
) else (
    echo.
    echo 잘못된 선택입니다. 1-4 중에서 선택해주세요.
    echo.
    goto select_version
)

echo.
echo 워치햄스터 런처를 종료합니다.
timeout /t 2 /nobreak > nul
exit /b 0