@echo off
REM ==========================================
REM POSCO 뉴스 모니터링 - 일회성 작업 실행
REM ==========================================
REM 
REM run_monitor.py를 사용한 일회성 작업 실행 스크립트
REM 빠른 상태 확인, 리포트 생성, 테스트 등에 사용
REM 
REM 사용법: 더블클릭으로 실행
REM 
REM 최종 수정: 2025-07-30 (역할 분리)
REM ==========================================

chcp 65001 > nul
title 🚀 POSCO 일회성 작업 실행
color 0B

cls
echo.
echo ========================================
echo   🚀 POSCO 뉴스 모니터링 - 일회성 작업
echo ========================================
echo.
echo 💡 24시간 지속 모니터링: POSCO_워치햄스터_시작.bat
echo 🚀 일회성 작업: 이 파일
echo.

cd /d "%~dp0"

REM Python 환경 확인
echo 🔍 Python 환경 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo 💡 Python 3.9 이상을 설치해주세요.
    pause
    exit /b 1
)

REM 의존성 확인
echo 🔍 의존성 확인 중...
python -c "import requests, psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 필요한 모듈이 없습니다. 자동 설치 중...
    pip install requests psutil
)

echo.
echo ========================================
echo   실행할 일회성 작업을 선택하세요:
echo ========================================
echo 1. 📊 현재 상태 체크 (빠른 일회성 상태 확인)
echo 2. 📈 영업일 비교 분석 (현재 vs 직전 영업일 상세 비교)
echo 3. 📋 일일 요약 리포트 (오늘 발행 뉴스 종합 요약)
echo 4. 📊 상세 분석 리포트 (각 뉴스별 상세 분석)
echo 5. 🔍 고급 분석 리포트 (30일 추이 및 패턴 분석)
echo 6. 🧪 알림 테스트 (워치햄스터 2.0 알림 시스템 테스트)
echo 7. 🎛️ 마스터 모니터 통합 체크 (전체 시스템 종합 분석)
echo 8. 🌆📈💱 개별 모니터 체크 (각 뉴스별 전용 모니터 실행)
echo.
set /p choice="선택 (1-8): "

echo.
echo 🚀 일회성 작업 실행 중...
echo ───────────────────────────────────────
python -u run_monitor.py %choice%

echo.
echo ───────────────────────────────────────
echo ✅ 일회성 작업 완료!
echo.
echo 💡 24시간 지속 모니터링이 필요하면:
echo    POSCO_워치햄스터_시작.bat을 실행하세요.
echo.
pause