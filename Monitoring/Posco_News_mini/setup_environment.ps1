# PowerShell 스크립트 - POSCO 뉴스 모니터 환경 설정
# UTF-8 인코딩 설정 (한글 깨짐 방지)
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null 2>&1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐹 POSCO 뉴스 모니터 환경 설정 🛡️" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python 버전 확인
Write-Host "🐍 Python 버전 확인 중..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다." -ForegroundColor Red
    Write-Host "Python 3.x를 설치하고 PATH에 추가해주세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""

# pip 업그레이드
Write-Host "📦 pip 업그레이드 중..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip | Out-Host
    Write-Host "✅ pip 업그레이드 완료" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ pip 업그레이드 실패 (계속 진행)" -ForegroundColor Yellow
}

Write-Host ""

# 필수 라이브러리 설치
Write-Host "📚 필수 라이브러리 설치 중..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    try {
        pip install -r requirements.txt | Out-Host
        Write-Host "✅ 라이브러리 설치 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 라이브러리 설치 실패" -ForegroundColor Red
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
} else {
    Write-Host "⚠️ requirements.txt 파일이 없습니다." -ForegroundColor Yellow
}

Write-Host ""

# 연결 테스트
Write-Host "🧪 연결 테스트 중..." -ForegroundColor Yellow
try {
    python run_monitor.py 6 | Out-Host
    Write-Host "✅ 연결 테스트 완료" -ForegroundColor Green
}
catch {
    Write-Host "❌ 연결 테스트 실패" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 환경 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 다음 단계:" -ForegroundColor Yellow
Write-Host "1. config.ps1에서 웹훅 URL 확인" -ForegroundColor White
Write-Host "2. 🚀POSCO뉴스_완전자동화_시작.ps1으로 워치햄스터 실행" -ForegroundColor White
Write-Host "3. 📊POSCO뉴스_워치햄스터_로그확인.ps1으로 로그 확인" -ForegroundColor White
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"