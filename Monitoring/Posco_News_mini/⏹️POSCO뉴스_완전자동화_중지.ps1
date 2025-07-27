# PowerShell 스크립트 - POSCO 뉴스 워치햄스터 중지
# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐹 POSCO 뉴스 모니터 - 완전 자동화 중지 🛡️" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🛑 워치햄스터 🛡️ 프로세스를 중지합니다..." -ForegroundColor Yellow

try {
    # 워치햄스터 프로세스 종료
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*monitor_WatchHamster.py*"
    } | Stop-Process -Force
    
    Write-Host "✅ 워치햄스터 프로세스 중지 완료" -ForegroundColor Green
    
    # 모니터링 프로세스 종료
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*run_monitor.py*"
    } | Stop-Process -Force
    
    Write-Host "✅ 모니터링 프로세스 중지 완료" -ForegroundColor Green
    
    # 로그 기록
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "WatchHamster.log" -Value "[$timestamp] 🛑 워치햄스터 및 모니터링 수동 중지 (PowerShell)"
    
    Write-Host ""
    Write-Host "🎉 모든 프로세스가 중지되었습니다." -ForegroundColor Green
}
catch {
    Write-Host "❌ 프로세스 중지 중 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "계속하려면 Enter를 누르세요"