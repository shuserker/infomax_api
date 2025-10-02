# WatchHamster 윈도우 PowerShell 실행 스크립트
# PowerShell에서 실행: .\run_windows.ps1

Write-Host "🐹 WatchHamster 윈도우 PowerShell 실행기" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# 현재 디렉토리로 이동
Set-Location $PSScriptRoot

# Python 설치 확인
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python 설치됨: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되지 않았습니다!" -ForegroundColor Red
    Write-Host "📥 Python 설치: https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# psutil 확인 및 설치
try {
    python -c "import psutil" 2>$null
    Write-Host "✅ psutil 사용 가능" -ForegroundColor Green
} catch {
    Write-Host "📦 psutil 설치 중..." -ForegroundColor Yellow
    pip install psutil
}

# tkinter 확인
try {
    python -c "import tkinter" 2>$null
    Write-Host "✅ tkinter 정상 - GUI 모드로 실행" -ForegroundColor Green
    Write-Host "🖥️ GUI 창이 열립니다..." -ForegroundColor Cyan
    
    # GUI 실행
    Start-Process python -ArgumentList "main_gui.py" -NoNewWindow
    
} catch {
    Write-Host "⚠️ tkinter 문제 감지 - 백엔드 모드로 실행" -ForegroundColor Yellow
    Write-Host "🔄 GUI 없이 모든 기능 제공" -ForegroundColor Cyan
    
    # 백엔드 실행
    python run_without_gui.py
}

Write-Host ""
Write-Host "🎊 WatchHamster 실행 완료!" -ForegroundColor Green
Read-Host "Press Enter to exit"