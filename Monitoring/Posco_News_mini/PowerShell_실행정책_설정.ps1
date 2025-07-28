# PowerShell 실행 정책 설정 스크립트
# 관리자 권한으로 실행해야 합니다.

# UTF-8 인코딩 설정
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null 2>&1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 PowerShell 실행 정책 설정" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ 관리자 권한이 필요합니다!" -ForegroundColor Red
    Write-Host "이 스크립트를 관리자 권한으로 실행해주세요." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host "✅ 관리자 권한으로 실행 중입니다." -ForegroundColor Green
Write-Host ""

# 현재 실행 정책 확인
Write-Host "📋 현재 PowerShell 실행 정책:" -ForegroundColor Yellow
$currentPolicy = Get-ExecutionPolicy
Write-Host "현재 정책: $currentPolicy" -ForegroundColor White
Write-Host ""

# 실행 정책 설정
Write-Host "🔧 PowerShell 실행 정책을 RemoteSigned로 설정합니다..." -ForegroundColor Yellow
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
    Write-Host "✅ 실행 정책 설정 완료!" -ForegroundColor Green
    
    # 설정 확인
    $newPolicy = Get-ExecutionPolicy
    Write-Host "새 정책: $newPolicy" -ForegroundColor Green
}
catch {
    Write-Host "❌ 실행 정책 설정 실패: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 PowerShell 실행 정책 설정 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 이제 다음 단계를 진행하세요:" -ForegroundColor Yellow
Write-Host "1. 🔧환경설정.bat 실행" -ForegroundColor White
Write-Host "2. 🚀POSCO뉴스_시작.bat 실행" -ForegroundColor White
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"