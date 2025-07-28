# PowerShell 스크립트 - POSCO 뉴스 워치햄스터 서비스 시작 (Windows 작업 스케줄러용)
# UTF-8 인코딩 설정 (한글 깨짐 방지)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

# 로그 기록
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "WatchHamster.log" -Value "[$timestamp] 🚀 워치햄스터 서비스 시작 (PowerShell)"

try {
    # 기존 프로세스가 있다면 종료
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*monitor_WatchHamster.py*"
    } | Stop-Process -Force
    
    # 워치햄스터 시작 (백그라운드)
    Start-Process python -ArgumentList "monitor_WatchHamster.py" -WindowStyle Hidden -WorkingDirectory $PSScriptRoot
    
    # 완료 로그
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "WatchHamster.log" -Value "[$timestamp] ✅ 워치햄스터 서비스 시작 완료 (PowerShell)"
}
catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path "WatchHamster.log" -Value "[$timestamp] ❌ 워치햄스터 서비스 시작 오류: $($_.Exception.Message)"
}