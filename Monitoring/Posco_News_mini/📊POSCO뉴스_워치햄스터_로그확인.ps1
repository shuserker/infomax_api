# PowerShell 스크립트 - POSCO 뉴스 워치햄스터 로그 확인
# UTF-8 인코딩 설정 (한글 깨짐 방지)
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null 2>&1

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐹 POSCO 뉴스 모니터 - 워치햄스터 🛡️ 로그" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 워치햄스터 로그 확인
if (Test-Path "WatchHamster.log") {
    Write-Host "📊 워치햄스터 로그 (최근 30줄):" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Get-Content "WatchHamster.log" -Tail 30 | ForEach-Object {
        if ($_ -match "❌|ERROR") {
            Write-Host $_ -ForegroundColor Red
        } elseif ($_ -match "✅|SUCCESS") {
            Write-Host $_ -ForegroundColor Green
        } elseif ($_ -match "🔍|🔄") {
            Write-Host $_ -ForegroundColor Cyan
        } else {
            Write-Host $_ -ForegroundColor White
        }
    }
    Write-Host "----------------------------------------" -ForegroundColor Gray
} else {
    Write-Host "📝 워치햄스터 로그 파일이 없습니다." -ForegroundColor Yellow
}

Write-Host ""

# 상태 파일 확인
if (Test-Path "WatchHamster_status.json") {
    Write-Host "📋 현재 상태:" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    $status = Get-Content "WatchHamster_status.json" | ConvertFrom-Json
    Write-Host "🕐 마지막 체크: $($status.last_check)" -ForegroundColor White
    Write-Host "🔄 모니터링 실행: $($status.monitor_running)" -ForegroundColor White
    Write-Host "📡 마지막 Git 체크: $($status.last_git_check)" -ForegroundColor White
    Write-Host "🆔 워치햄스터 PID: $($status.watchdog_pid)" -ForegroundColor White
    Write-Host "----------------------------------------" -ForegroundColor Gray
} else {
    Write-Host "📝 상태 파일이 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 사용 가능한 명령어:" -ForegroundColor Yellow
Write-Host "- 🚀POSCO뉴스_완전자동화_시작.ps1 : 완전 자동화 시작" -ForegroundColor White
Write-Host "- ⏹️POSCO뉴스_완전자동화_중지.ps1  : 완전 자동화 중지" -ForegroundColor White
Write-Host "- 📊POSCO뉴스_워치햄스터_로그확인.ps1 : 로그 확인" -ForegroundColor White
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"