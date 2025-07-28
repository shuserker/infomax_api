# PowerShell 한글 깨짐 해결 실행 스크립트
# 이 스크립트를 통해 다른 PowerShell 스크립트를 실행하면 한글이 정상 표시됩니다.

# UTF-8 인코딩 강제 설정
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null 2>&1

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 PowerShell 한글 깨짐 해결 실행기 🔧" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 실행 가능한 스크립트:" -ForegroundColor Yellow
Write-Host "1. 🚀 POSCO뉴스 완전자동화 시작" -ForegroundColor White
Write-Host "2. ⏹️ POSCO뉴스 완전자동화 중지" -ForegroundColor White
Write-Host "3. 📊 워치햄스터 로그 확인" -ForegroundColor White
Write-Host "4. 🔧 환경 설정" -ForegroundColor White
Write-Host "5. 🔧 PowerShell 실행 정책 설정 (관리자 권한 필요)" -ForegroundColor Yellow
Write-Host "0. 종료" -ForegroundColor Gray
Write-Host ""

do {
    $choice = Read-Host "실행할 스크립트 번호를 입력하세요 (0-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "🚀 POSCO뉴스 완전자동화를 시작합니다..." -ForegroundColor Green
            & ".\🚀POSCO뉴스_완전자동화_시작.ps1"
        }
        "2" {
            Write-Host "⏹️ POSCO뉴스 완전자동화를 중지합니다..." -ForegroundColor Red
            & ".\⏹️POSCO뉴스_완전자동화_중지.ps1"
        }
        "3" {
            Write-Host "📊 워치햄스터 로그를 확인합니다..." -ForegroundColor Cyan
            & ".\📊POSCO뉴스_워치햄스터_로그확인.ps1"
        }
        "4" {
            Write-Host "🔧 환경 설정을 시작합니다..." -ForegroundColor Yellow
            & ".\setup_environment.ps1"
        }
        "5" {
            Write-Host "🔧 PowerShell 실행 정책을 설정합니다..." -ForegroundColor Yellow
            Write-Host "⚠️ 관리자 권한이 필요합니다. 관리자 권한으로 다시 실행됩니다." -ForegroundColor Red
            Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSScriptRoot\PowerShell_실행정책_설정.ps1`"" -Verb RunAs
        }
        "0" {
            Write-Host "👋 종료합니다." -ForegroundColor Gray
            break
        }
        default {
            Write-Host "❌ 잘못된 선택입니다. 0-5 사이의 숫자를 입력해주세요." -ForegroundColor Red
        }
    }
    
    if ($choice -ne "0") {
        Write-Host ""
        Write-Host "계속하려면 Enter를 누르세요..." -ForegroundColor Gray
        Read-Host
        Write-Host ""
    }
    
} while ($choice -ne "0")