# PowerShell 스크립트 - POSCO 뉴스 워치햄스터 시작
# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐹 POSCO 뉴스 모니터 - 완전 자동화 시작 🛡️" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🐹 워치햄스터 🛡️ 기능:" -ForegroundColor Yellow
Write-Host "- 모니터링 프로세스 자동 감시" -ForegroundColor White
Write-Host "- Git 업데이트 자동 체크 (1시간 간격)" -ForegroundColor White
Write-Host "- 프로세스 오류 시 자동 재시작" -ForegroundColor White
Write-Host "- 상태 알림 전송" -ForegroundColor White
Write-Host ""

Write-Host "중단하려면 Ctrl+C를 누르세요" -ForegroundColor Red
Write-Host ""

try {
    # Python 스크립트 실행
    python monitor_WatchHamster.py
}
catch {
    Write-Host "❌ 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "🐹 워치햄스터 🛡️가 중단되었습니다." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
}