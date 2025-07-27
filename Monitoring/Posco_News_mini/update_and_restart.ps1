# PowerShell 스크립트 - POSCO 뉴스 모니터 업데이트 및 재시작
# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔄 POSCO 뉴스 모니터 업데이트 및 재시작" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 모니터링 중지
Write-Host "⏹️ 현재 모니터링 중지 중..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*monitor_WatchHamster.py*" -or $_.CommandLine -like "*run_monitor.py*"
    } | Stop-Process -Force
    Write-Host "✅ 모니터링 중지 완료" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ 실행 중인 프로세스가 없습니다." -ForegroundColor Yellow
}

Write-Host ""

# Git에서 최신 코드 가져오기
Write-Host "📥 Git에서 최신 코드 가져오는 중..." -ForegroundColor Yellow
try {
    $gitResult = git pull origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git pull 성공" -ForegroundColor Green
        Write-Host $gitResult -ForegroundColor White
    } else {
        Write-Host "❌ Git pull 실패!" -ForegroundColor Red
        Write-Host $gitResult -ForegroundColor Red
        Write-Host "수동으로 확인해주세요." -ForegroundColor Yellow
        Read-Host "계속하려면 Enter를 누르세요"
        exit 1
    }
}
catch {
    Write-Host "❌ Git 명령 실행 오류: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""

# 모니터링 재시작
Write-Host "🚀 업데이트 완료! 모니터링 재시작 중..." -ForegroundColor Yellow
try {
    Start-Process PowerShell -ArgumentList "-File", "🚀POSCO뉴스_완전자동화_시작.ps1" -WorkingDirectory $PSScriptRoot
    Write-Host "✅ 모니터링 재시작 완료" -ForegroundColor Green
}
catch {
    Write-Host "❌ 모니터링 재시작 실패: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 업데이트 및 재시작 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"