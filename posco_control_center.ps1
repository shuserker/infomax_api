# ============================================================================
# POSCO Control Center v4.0
# Windows용 PowerShell POSCO 뉴스 및 주가 모니터링 제어 센터
# ============================================================================

# 스크립트 경로 설정
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# 공통 라이브러리 로드
if (Test-Path ".\lib_wt_common.ps1") {
    . ".\lib_wt_common.ps1"
} else {
    Write-Host "Error: lib_wt_common.ps1를 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "현재 경로: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "스크립트 경로: $SCRIPT_DIR" -ForegroundColor Yellow
    exit 1
}

# 초기화
Initialize-System

# ============================================================================
# 메인 메뉴
# ============================================================================
function Show-MainMenu {
    Clear-Host
    Show-Header "🏭 POSCO Control Center v4.0 🎛️"
    Write-Host "🎯 POSCO 뉴스 및 주가 모니터링 시스템을 관리합니다" -ForegroundColor $INFO
    Write-Host ""

    Write-Host "🎛️ 관리할 기능을 선택하세요:" -ForegroundColor $YELLOW
    Write-Host ""

    # 모니터링 관리
    Start-Box $GREEN
    Write-Host "║                           📊 모니터링 관리                                    ║" -ForegroundColor $CYAN
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $GREEN
    Show-MenuItem "1." "🚀 워치햄스터 시작" "POSCO 뉴스 모니터링 시작"
    Show-MenuItem "2." "🛑 워치햄스터 중지" "모니터링 프로세스 중지"
    Show-MenuItem "3." "🔄 워치햄스터 재시작" "모니터링 시스템 재시작"
    Show-MenuItem "4." "📊 실시간 상태 확인" "현재 모니터링 상태 확인"
    End-Box

    Write-Host ""

    # 뉴스 관리
    Start-Box $BLUE
    Write-Host "║                           📰 뉴스 관리                                      ║" -ForegroundColor $MAGENTA
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $BLUE
    Show-MenuItem "A." "📋 뉴스 로그 확인" "최신 뉴스 로그 확인"
    Show-MenuItem "B." "📈 뉴스 통계 보기" "뉴스 수집 통계 확인"
    Show-MenuItem "C." "🔍 뉴스 검색" "특정 키워드 뉴스 검색"
    End-Box

    Write-Host ""

    # 시스템 관리
    Start-Box $RED
    Write-Host "║                           ⚙️ 시스템 관리                                      ║" -ForegroundColor $WHITE
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $RED
    Show-MenuItem "D." "🔧 시스템 상태" "POSCO 시스템 상태 확인"
    Show-MenuItem "E." "🧪 시스템 테스트" "모니터링 시스템 테스트"
    Show-MenuItem "F." "📦 데이터 백업" "뉴스 데이터 백업"
    End-Box

    Write-Host ""
    Write-Host "0. ❌ 메인 메뉴로 돌아가기" -ForegroundColor $GRAY
    Write-Host ""

    Show-SystemInfo

    $choice = Read-Host "🎯 선택하세요 (1-4, A-F, 0)"

    switch ($choice) {
        "1" { Start-WatchHamster }
        "2" { Stop-WatchHamster }
        "3" { Restart-WatchHamster }
        "4" { Show-MonitoringStatus }
        "A" { Show-NewsLogs }
        "B" { Show-NewsStats }
        "C" { Search-News }
        "D" { Show-SystemStatus }
        "E" { Start-SystemTest }
        "F" { Start-DataBackup }
        "0" { Return-ToMain }
        default { Show-InvalidChoice }
    }
}

# ============================================================================
# 모니터링 관리
# ============================================================================

# 워치햄스터 시작
function Start-WatchHamster {
    Clear-Host
    Show-Header "🚀 워치햄스터 시작"
    
    if (!(Confirm-Action "POSCO 뉴스 모니터링을 시작하시겠습니까?")) {
        Show-MainMenu
        return
    }

    # 이미 실행 중인지 확인
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*monitor_WatchHamster.py*" }
    if ($processes) {
        Show-Warning "🐹 POSCO 워치햄스터가 이미 실행 중입니다."
        Write-Host ""
        Read-Host "계속하려면 Enter를 누르세요"
        Show-MainMenu
        return
    }

    # Python 스크립트 실행
    if (Test-Path "Monitoring\Posco_News_mini\monitor_WatchHamster.py") {
        Set-Location "Monitoring\Posco_News_mini"
        Start-Process -FilePath "python" -ArgumentList "monitor_WatchHamster.py" -WindowStyle Hidden -RedirectStandardOutput "..\..\posco_monitor.log" -RedirectStandardError "..\..\posco_monitor.log"
        Set-Location $SCRIPT_DIR
        Start-Sleep -Seconds 3
        
        # 프로세스 확인
        $newProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*monitor_WatchHamster.py*" }
        if ($newProcesses) {
            Show-Success "🐹 POSCO 워치햄스터가 성공적으로 시작되었습니다."
            Show-Info "🛡️ 자동 복구 기능이 활성화되었습니다."
            Show-Info "📊 프로세스 감시: 5분 간격"
            Show-Info "🔄 Git 업데이트 체크: 60분 간격"
            Show-Info "📋 정기 상태 알림: 2시간 간격"
            Show-Info "🌙 조용한 모드: 18시 이후 문제 발생 시에만 알림"
        } else {
            Show-Error "워치햄스터 시작에 실패했습니다."
        }
    } else {
        Show-Error "monitor_WatchHamster.py 파일을 찾을 수 없습니다."
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 워치햄스터 중지
function Stop-WatchHamster {
    Clear-Host
    Show-Header "🛑 워치햄스터 중지"
    
    if (!(Confirm-Action "POSCO 뉴스 모니터링을 중지하시겠습니까?")) {
        Show-MainMenu
        return
    }

    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*monitor_WatchHamster.py*" }
    
    if ($processes) {
        foreach ($process in $processes) {
            Stop-Process -Id $process.Id -Force
        }
        Start-Sleep -Seconds 2
        
        Show-Success "🐹 POSCO 워치햄스터가 성공적으로 중지되었습니다."
    } else {
        Show-Info "실행 중인 워치햄스터가 없습니다."
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 워치햄스터 재시작
function Restart-WatchHamster {
    Clear-Host
    Show-Header "🔄 워치햄스터 재시작"
    
    if (!(Confirm-Action "워치햄스터를 재시작하시겠습니까?")) {
        Show-MainMenu
        return
    }

    Stop-WatchHamster
    Start-Sleep -Seconds 2
    Start-WatchHamster
}

# 실시간 상태 확인
function Show-MonitoringStatus {
    Clear-Host
    Show-Header "📊 실시간 상태 확인"
    
    Show-Section "⚙️ 프로세스 상태"
    
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*monitor_WatchHamster.py*" }
    if ($processes) {
        Show-Success "🐹 POSCO 워치햄스터가 실행 중입니다."
        foreach ($process in $processes) {
            $startTime = $process.StartTime
            $runtime = (Get-Date) - $startTime
            Write-Host "  • PID: $($process.Id), 실행시간: $($runtime.ToString('hh\:mm\:ss'))" -ForegroundColor $GRAY
        }
    } else {
        Show-Warning "🐹 POSCO 워치햄스터가 실행되지 않았습니다."
    }

    Show-Section "📊 시스템 리소스"
    Show-SystemInfo

    Show-Section "📁 로그 파일 상태"
    
    $logFiles = @("posco_monitor.log", "system.log", "error.log")
    foreach ($logFile in $logFiles) {
        if (Test-Path $logFile) {
            $fileInfo = Get-Item $logFile
            $size = [math]::Round($fileInfo.Length / 1KB, 1)
            $modified = $fileInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "✅ $logFile (${size}KB, 수정: $modified)" -ForegroundColor $GREEN
        } else {
            Write-Host "❌ $logFile (없음)" -ForegroundColor $RED
        }
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 뉴스 관리
# ============================================================================

# 뉴스 로그 확인
function Show-NewsLogs {
    Clear-Host
    Show-Header "📋 뉴스 로그 확인"
    
    if (Test-Path "posco_monitor.log") {
        Write-Host "최근 20줄의 로그:" -ForegroundColor $CYAN
        Write-Host ""
        Get-Content "posco_monitor.log" -Tail 20
    } else {
        Show-Warning "로그 파일이 없습니다."
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 뉴스 통계 보기
function Show-NewsStats {
    Clear-Host
    Show-Header "📈 뉴스 통계 보기"
    
    if (Test-Path "posco_news_data.json") {
        $fileInfo = Get-Item "posco_news_data.json"
        $size = [math]::Round($fileInfo.Length / 1KB, 1)
        $modified = $fileInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "✅ posco_news_data.json (${size}KB, 수정: $modified)" -ForegroundColor $GREEN
        
        # 간단한 통계
        try {
            $jsonContent = Get-Content "posco_news_data.json" | ConvertFrom-Json
            if ($jsonContent -is [array]) {
                Write-Host "  총 뉴스 수: $($jsonContent.Count)개" -ForegroundColor $WHITE
            } else {
                Write-Host "  데이터 형식: 객체" -ForegroundColor $WHITE
            }
        }
        catch {
            Write-Host "  통계 분석 실패" -ForegroundColor $RED
        }
    } else {
        Write-Host "❌ posco_news_data.json (없음)" -ForegroundColor $RED
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 뉴스 검색
function Search-News {
    Clear-Host
    Show-Header "🔍 뉴스 검색"
    
    $keyword = Read-Host "검색할 키워드를 입력하세요"
    
    if ([string]::IsNullOrEmpty($keyword)) {
        Show-Error "키워드를 입력해주세요."
        Write-Host ""
        Read-Host "계속하려면 Enter를 누르세요"
        Show-MainMenu
        return
    }

    if (Test-Path "posco_news_data.json") {
        Write-Host "검색 결과:" -ForegroundColor $CYAN
        Write-Host ""
        try {
            $jsonContent = Get-Content "posco_news_data.json" | ConvertFrom-Json
            if ($jsonContent -is [array]) {
                $results = $jsonContent | Where-Object { 
                    $_.title -like "*$keyword*" -or $_.content -like "*$keyword*" 
                }
                Write-Host "발견된 뉴스: $($results.Count)개" -ForegroundColor $WHITE
                for ($i = 0; $i -lt [math]::Min(5, $results.Count); $i++) {
                    Write-Host "$($i+1). $($results[$i].title)" -ForegroundColor $WHITE
                    Write-Host "   날짜: $($results[$i].date)" -ForegroundColor $GRAY
                    Write-Host ""
                }
            }
        }
        catch {
            Write-Host "검색 오류: $($_.Exception.Message)" -ForegroundColor $RED
        }
    } else {
        Show-Warning "뉴스 데이터 파일이 없습니다."
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 시스템 관리
# ============================================================================

# 시스템 상태 확인
function Show-SystemStatus {
    Clear-Host
    Show-Header "🔧 시스템 상태 확인"
    
    Show-Section "📊 POSCO 시스템 현황"
    
    # Python 환경 확인
    Show-Section "🐍 Python 환경"
    Test-PythonEnvironment
    
    # 필수 파일 확인
    Show-Section "📁 필수 파일 확인"
    $requiredFiles = @("Monitoring\Posco_News_mini\monitor_WatchHamster.py", "Monitoring\Posco_News_mini\config.py", "requirements.txt")
    Test-RequiredFiles $requiredFiles
    
    # 데이터 파일 확인
    Show-Section "📊 데이터 파일 상태"
    $dataFiles = @("posco_news_data.json", "posco_news_cache.json")
    foreach ($dataFile in $dataFiles) {
        if (Test-Path $dataFile) {
            $fileInfo = Get-Item $dataFile
            $size = [math]::Round($fileInfo.Length / 1KB, 1)
            $modified = $fileInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "✅ $dataFile (${size}KB, 수정: $modified)" -ForegroundColor $GREEN
        } else {
            Write-Host "❌ $dataFile (없음)" -ForegroundColor $RED
        }
    }
    
    # 네트워크 연결 확인
    Show-Section "🌐 네트워크 상태"
    Test-NetworkConnection
    
    # 시스템 리소스 확인
    Show-Section "💻 시스템 리소스"
    Show-SystemInfo

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 시스템 테스트
function Start-SystemTest {
    Clear-Host
    Show-Header "🧪 시스템 테스트"
    
    if (!(Confirm-Action "POSCO 모니터링 시스템 테스트를 실행하시겠습니까?")) {
        Show-MainMenu
        return
    }

    Write-Host "시스템 테스트를 진행하고 있습니다..." -ForegroundColor $INFO

    Show-Section "🔍 기본 시스템 테스트"
    
    # Python 환경 테스트
    if (Test-PythonEnvironment) {
        Show-Success "Python 환경 테스트 통과"
    } else {
        Show-Error "Python 환경 테스트 실패"
    }
    
    # 네트워크 연결 테스트
    if (Test-NetworkConnection) {
        Show-Success "네트워크 연결 테스트 통과"
    } else {
        Show-Error "네트워크 연결 테스트 실패"
    }
    
    # 파일 시스템 테스트
    $testFiles = @("Monitoring\Posco_News_mini\monitor_WatchHamster.py")
    if (Test-RequiredFiles $testFiles) {
        Show-Success "파일 시스템 테스트 통과"
    } else {
        Show-Error "파일 시스템 테스트 실패"
    }
    
    # Python 스크립트 테스트
    Show-Section "🐍 Python 스크립트 테스트"
    if (Test-Path "Monitoring\Posco_News_mini\monitor_WatchHamster.py") {
        try {
            python -c "import sys; print('Python 스크립트 테스트 통과')" 2>$null
            Show-Success "🐹 POSCO 워치햄스터 테스트 통과"
        }
        catch {
            Show-Error "🐹 POSCO 워치햄스터 테스트 실패"
        }
    } else {
        Show-Warning "🐹 POSCO 워치햄스터 파일이 없습니다."
    }

    Show-Success "시스템 테스트가 완료되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# 데이터 백업
function Start-DataBackup {
    Clear-Host
    Show-Header "📦 데이터 백업"
    
    if (!(Confirm-Action "POSCO 뉴스 데이터를 백업하시겠습니까?")) {
        Show-MainMenu
        return
    }

    $backupDir = "$env:USERPROFILE\.watchhamster\posco_backups"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "posco_backup_$timestamp"
    $backupPath = "$backupDir\$backupName"

    if (!(Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }

    Write-Host "데이터를 백업하고 있습니다..." -ForegroundColor $INFO

    # 중요 데이터 파일들 백업
    $dataFiles = @("posco_news_data.json", "posco_news_cache.json", "*.py", "config.py")
    $backedUp = $false
    
    foreach ($pattern in $dataFiles) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $destPath = "$backupPath\$($file.Name)"
            Copy-Item $file.FullName $destPath -Force
            $backedUp = $true
        }
    }

    # 백업 압축
    if ($backedUp) {
        Set-Location $backupDir
        Compress-Archive -Path $backupName -DestinationPath "$backupName.zip" -Force
        Remove-Item $backupName -Recurse -Force
        Set-Location $SCRIPT_DIR
        
        $backupSize = [math]::Round((Get-Item "$backupDir\$backupName.zip").Length / 1KB, 1)
        Show-Success "백업이 생성되었습니다: $backupName.zip (크기: ${backupSize}KB)"
    } else {
        Show-Error "백업할 데이터가 없습니다."
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 유틸리티 함수들
# ============================================================================

# 잘못된 선택 처리
function Show-InvalidChoice {
    Show-Error "잘못된 선택입니다. 다시 시도해주세요."
    Start-Sleep -Seconds 2
    Show-MainMenu
}

# 메인 메뉴로 돌아가기
function Return-ToMain {
    Set-Location $SCRIPT_DIR
    if (Test-Path "..\watchhamster_master_control.ps1") {
        & "..\watchhamster_master_control.ps1"
    } else {
        Show-Error "메인 제어 센터를 찾을 수 없습니다."
        exit 1
    }
}

# ============================================================================
# 메인 실행
# ============================================================================

# 스크립트 시작
Show-MainMenu 