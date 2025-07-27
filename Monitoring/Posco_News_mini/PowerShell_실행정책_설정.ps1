# PowerShell 실행 정책 설정 스크립트
# 관리자 권한으로 실행 필요

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 PowerShell 실행 정책 설정" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ 이 스크립트는 관리자 권한으로 실행해야 합니다." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 수동 설정 방법:" -ForegroundColor Yellow
    Write-Host "1. PowerShell을 관리자 권한으로 실행" -ForegroundColor White
    Write-Host "2. 다음 명령어 실행:" -ForegroundColor White
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host "🔐 현재 실행 정책 확인 중..." -ForegroundColor Yellow
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "현재 정책: $currentPolicy" -ForegroundColor White

Write-Host ""

if ($currentPolicy -eq "RemoteSigned" -or $currentPolicy -eq "Unrestricted") {
    Write-Host "✅ 실행 정책이 이미 올바르게 설정되어 있습니다." -ForegroundColor Green
} else {
    Write-Host "🔧 실행 정책을 RemoteSigned로 변경 중..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ 실행 정책 변경 완료" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ 실행 정책 변경 실패: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "📋 수동 설정 방법:" -ForegroundColor Yellow
        Write-Host "PowerShell 관리자 모드에서 다음 명령어 실행:" -ForegroundColor White
        Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 PowerShell 설정 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 이제 다음 스크립트들을 실행할 수 있습니다:" -ForegroundColor Yellow
Write-Host "- setup_environment.ps1 : 환경 설정" -ForegroundColor White
Write-Host "- 🚀POSCO뉴스_완전자동화_시작.ps1 : 워치햄스터 시작" -ForegroundColor White
Write-Host ""

Read-Host "계속하려면 Enter를 누르세요"