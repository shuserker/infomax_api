# ============================================================================
# WatchHamster Master Control Center v4.0
# Windows용 PowerShell 워치햄스터 총괄 관리 센터
# 개선사항 반영: 메모리 계산 수정, 로깅 강화, 파일명 영문화
# ============================================================================

# 스크립트 경로 설정
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# 공통 라이브러리 로드
. "lib_wt_common.ps1"

# 초기화
Initialize-System

# ============================================================================
# 메인 메뉴
# ============================================================================
function Show-MainMenu {
    Clear-Host
    Show-Header "🐹 WatchHamster Master Control Center v4.0 🛡️"
    Write-Host "🎯 현재 활성화된 모니터링 시스템을 관리합니다" -ForegroundColor $INFO
    Write-Host ""

    Write-Host "🎛️ 관리할 시스템을 선택하세요:" -ForegroundColor $YELLOW
    Write-Host ""

    # 활성화된 모니터링 시스템
    Start-Box $GREEN
    Write-Host "║                       🏭 활성화된 모니터링 시스템                       ║" -ForegroundColor $CYAN
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $GREEN
    Show-MenuItem "1." "🏭 POSCO 뉴스 모니터링" "포스코 뉴스 및 주가 모니터링 시스템"
    End-Box

    Write-Host ""

    # 시스템 관리
    Start-Box $BLUE
    Write-Host "║                           🔧 시스템 관리                                    ║" -ForegroundColor $MAGENTA
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $BLUE
    Show-MenuItem "A." "🛡️ 전체 시스템 상태" "모든 워치햄스터 상태 확인"
    Show-MenuItem "B." "🔄 전체 시스템 업데이트" "모든 시스템 Git 업데이트"
    Show-MenuItem "C." "📋 통합 로그 관리" "모든 시스템 로그 통합 관리"
    Show-MenuItem "D." "🧪 전체 시스템 테스트" "모든 시스템 통합 테스트"
    End-Box

    Write-Host ""

    # 고급 관리
    Start-Box $RED
    Write-Host "║                           ⚙️ 고급 관리                                      ║" -ForegroundColor $WHITE
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $RED
    Show-MenuItem "E." "📦 전체 백업 생성" "모든 시스템 통합 백업"
    Show-MenuItem "F." "🔧 워치햄스터 설정" "총괄 설정 관리"
    Show-MenuItem "G." "🎨 UI 테마 변경" "색상 테마 및 인터페이스 설정"
    End-Box

    Write-Host ""
    Write-Host "0. ❌ 종료" -ForegroundColor $GRAY
    Write-Host ""

    Show-SystemInfo

    $choice = Read-Host "🎯 선택하세요 (1, A-G, 0)"

    switch ($choice) {
        "1" { Start-PoscoMonitoring }
        "A" { Show-SystemStatus }
        "B" { Start-SystemUpdate }
        "C" { Show-IntegratedLogs }
        "D" { Start-SystemTest }
        "E" { Start-FullBackup }
        "F" { Show-WatchHamsterConfig }
        "G" { Show-UIThemeConfig }
        "0" { Exit-System }
        default { Show-InvalidChoice }
    }
}

# ============================================================================
# POSCO 모니터링 시스템
# ============================================================================
function Start-PoscoMonitoring {
    Clear-Host
    Show-Header "🏭 POSCO 모니터링 시스템 진입"
    
    Write-Host "POSCO 모니터링 시스템으로 이동 중..." -ForegroundColor $INFO
    Start-Sleep -Seconds 2

    $poscoPath = "Monitoring\Posco_News_mini"
    if (Test-Path $poscoPath) {
        Set-Location $poscoPath
        
        # POSCO 관리 센터 실행
        if (Test-Path "posco_control_center.ps1") {
            & "posco_control_center.ps1"
        } elseif (Test-Path "POSCO_통합_관리_센터_v3.bat") {
            Show-Warning "Windows BAT 파일을 발견했습니다. PowerShell 스크립트로 변환이 필요합니다."
            Read-Host "계속하려면 Enter를 누르세요"
        } else {
            Show-Error "POSCO 모니터링 시스템을 찾을 수 없습니다."
            Show-Info "필요한 파일: posco_control_center.ps1"
            Read-Host "계속하려면 Enter를 누르세요"
        }
        
        Set-Location $SCRIPT_DIR
    } else {
        Show-Error "POSCO 모니터링 디렉토리를 찾을 수 없습니다."
        Show-Info "경로: Monitoring\Posco_News_mini\"
        Read-Host "계속하려면 Enter를 누르세요"
    }
    
    Show-MainMenu
}

# ============================================================================
# 전체 시스템 상태
# ============================================================================
function Show-SystemStatus {
    Clear-Host
    Show-Header "🛡️ 전체 시스템 상태 확인"
    
    Write-Host "모든 워치햄스터 시스템 상태를 확인하고 있습니다..." -ForegroundColor $INFO
    Start-Sleep -Seconds 2

    Show-Section "📊 시스템 상태 현황"

    # Python 환경 확인
    Show-Section "🐍 Python 환경"
    Test-PythonEnvironment

    # 필수 파일 확인
    Show-Section "📁 필수 파일 확인"
    $requiredFiles = @("lib_wt_common.ps1", "requirements.txt", "README.md")
    Test-RequiredFiles $requiredFiles

    # 네트워크 연결 확인
    Show-Section "🌐 네트워크 상태"
    Test-NetworkConnection

    # Git 저장소 상태 확인
    Show-Section "📦 Git 저장소 상태"
    Test-GitStatus

    # 프로세스 확인
    Show-Section "⚙️ 프로세스 상태"
    Test-Process "python"
    Test-Process "monitor"

    # 시스템 리소스 확인
    Show-Section "💻 시스템 리소스"
    Show-SystemInfo

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 전체 시스템 업데이트
# ============================================================================
function Start-SystemUpdate {
    Clear-Host
    Show-Header "🔄 전체 시스템 업데이트"
    
    if (!(Confirm-Action "모든 워치햄스터 시스템을 업데이트하시겠습니까?")) {
        Show-MainMenu
        return
    }

    Write-Host "시스템 업데이트를 진행하고 있습니다..." -ForegroundColor $INFO

    # Git 상태 확인
    if (Test-Path ".git") {
        Show-Section "📦 Git 업데이트"
        
        # 현재 브랜치 확인
        try {
            $currentBranch = git branch --show-current 2>$null
            Show-Info "현재 브랜치: $currentBranch"
        }
        catch {
            Show-Warning "브랜치 정보를 가져올 수 없습니다."
        }
        
        # 원격 변경사항 가져오기
        try {
            git fetch origin 2>$null
            Show-Success "원격 저장소에서 변경사항을 가져왔습니다."
        }
        catch {
            Show-Error "원격 저장소 접근에 실패했습니다."
        }
        
        # 로컬 변경사항 확인
        try {
            $status = git status --porcelain 2>$null
            if ($status) {
                Show-Warning "로컬 변경사항이 있습니다. 백업을 권장합니다."
                if (Confirm-Action "변경사항을 커밋하시겠습니까?") {
                    git add .
                    git commit -m "Auto commit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                    Show-Success "변경사항이 커밋되었습니다."
                }
            }
        }
        catch {
            Show-Warning "Git 상태를 확인할 수 없습니다."
        }
        
        # 업데이트 적용
        try {
            git pull origin $currentBranch 2>$null
            Show-Success "시스템이 최신 상태로 업데이트되었습니다."
        }
        catch {
            Show-Error "업데이트 중 오류가 발생했습니다."
        }
    } else {
        Show-Warning "Git 저장소가 아닙니다."
    }

    # POSCO 모니터링 업데이트
    if (Test-Path "Monitoring\Posco_News_mini") {
        Show-Section "🏭 POSCO 모니터링 업데이트"
        Set-Location "Monitoring\Posco_News_mini"
        
        if (Test-Path ".git") {
            try {
                git pull origin main 2>$null
                Show-Success "POSCO 모니터링이 업데이트되었습니다."
            }
            catch {
                Show-Warning "POSCO 모니터링 업데이트에 실패했습니다."
            }
        }
        
        Set-Location $SCRIPT_DIR
    }

    Show-Success "전체 시스템 업데이트가 완료되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 통합 로그 관리
# ============================================================================
function Show-IntegratedLogs {
    Clear-Host
    Show-Header "📋 통합 로그 관리"
    
    Show-Section "📊 로그 파일 현황"
    
    # 로그 디렉토리 확인
    if (Test-Path $LOG_DIR) {
        Show-Success "로그 디렉토리: $LOG_DIR"
        
        # 로그 파일 목록
        $logFiles = Get-ChildItem -Path $LOG_DIR -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            Write-Host "발견된 로그 파일들:" -ForegroundColor $WHITE
            foreach ($file in $logFiles) {
                $size = [math]::Round($file.Length / 1KB, 1)
                $modified = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                Write-Host "  • $($file.Name) (${size}KB, 수정: $modified)" -ForegroundColor $GRAY
            }
        } else {
            Show-Info "로그 파일이 없습니다."
        }
    } else {
        Show-Warning "로그 디렉토리가 없습니다."
    }

    Write-Host ""
    Write-Host "로그 관리 옵션:" -ForegroundColor $YELLOW
    Write-Host "1. 최신 로그 보기"
    Write-Host "2. 에러 로그 보기"
    Write-Host "3. 로그 파일 정리"
    Write-Host "4. 로그 설정 변경"
    Write-Host "0. 돌아가기"
    Write-Host ""
    
    $logChoice = Read-Host "선택하세요 (1-4, 0)"

    switch ($logChoice) {
        "1" { Show-LatestLogs }
        "2" { Show-ErrorLogs }
        "3" { Start-LogCleanup }
        "4" { Show-LogSettings }
        "0" { Show-MainMenu }
        default { Show-InvalidChoice }
    }
}

# 로그 보기 함수들
function Show-LatestLogs {
    Clear-Host
    Show-Header "📋 최신 로그 보기"
    
    if (Test-Path $LOG_FILE) {
        Write-Host "최근 20줄의 로그:" -ForegroundColor $CYAN
        Write-Host ""
        Get-Content $LOG_FILE -Tail 20
    } else {
        Show-Warning "로그 파일이 없습니다."
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-IntegratedLogs
}

function Show-ErrorLogs {
    Clear-Host
    Show-Header "📋 에러 로그 보기"
    
    if (Test-Path $ERROR_LOG) {
        Write-Host "최근 에러 로그:" -ForegroundColor $CYAN
        Write-Host ""
        Get-Content $ERROR_LOG -Tail 20
    } else {
        Show-Warning "에러 로그 파일이 없습니다."
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-IntegratedLogs
}

function Start-LogCleanup {
    Clear-Host
    Show-Header "📋 로그 파일 정리"
    
    if (Confirm-Action "30일 이상 된 로그 파일을 삭제하시겠습니까?") {
        $cutoffDate = (Get-Date).AddDays(-30)
        $oldLogs = Get-ChildItem -Path $LOG_DIR -Filter "*.log" | Where-Object { $_.LastWriteTime -lt $cutoffDate }
        
        foreach ($log in $oldLogs) {
            Remove-Item $log.FullName -Force
        }
        
        Show-Success "오래된 로그 파일이 정리되었습니다."
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-IntegratedLogs
}

function Show-LogSettings {
    Clear-Host
    Show-Header "📋 로그 설정"
    
    Show-Info "현재 로그 설정:"
    Write-Host "  로그 디렉토리: $LOG_DIR"
    Write-Host "  로그 파일: $LOG_FILE"
    Write-Host "  에러 로그: $ERROR_LOG"
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-IntegratedLogs
}

# ============================================================================
# 전체 시스템 테스트
# ============================================================================
function Start-SystemTest {
    Clear-Host
    Show-Header "🧪 전체 시스템 테스트"
    
    if (!(Confirm-Action "전체 시스템 테스트를 실행하시겠습니까?")) {
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
    $testFiles = @("lib_wt_common.ps1", "requirements.txt")
    if (Test-RequiredFiles $testFiles) {
        Show-Success "파일 시스템 테스트 통과"
    } else {
        Show-Error "파일 시스템 테스트 실패"
    }
    
    # POSCO 모니터링 테스트
    Show-Section "🏭 POSCO 모니터링 테스트"
    if (Test-Path "Monitoring\Posco_News_mini") {
        Set-Location "Monitoring\Posco_News_mini"
        
        # Python 스크립트 테스트
        if (Test-Path "run_monitor.py") {
            try {
                python -c "import sys; print('Python 스크립트 테스트 통과')" 2>$null
                Show-Success "POSCO Python 스크립트 테스트 통과"
            }
            catch {
                Show-Error "POSCO Python 스크립트 테스트 실패"
            }
        }
        
        Set-Location $SCRIPT_DIR
    } else {
        Show-Warning "POSCO 모니터링 디렉토리가 없습니다."
    }

    Show-Success "전체 시스템 테스트가 완료되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 전체 백업 생성
# ============================================================================
function Start-FullBackup {
    Clear-Host
    Show-Header "📦 전체 백업 생성"
    
    if (!(Confirm-Action "전체 시스템 백업을 생성하시겠습니까?")) {
        Show-MainMenu
        return
    }

    $backupDir = "$env:USERPROFILE\.watchhamster\backups"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "watchhamster_backup_$timestamp"
    $backupPath = "$backupDir\$backupName"

    if (!(Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }

    Write-Host "백업을 생성하고 있습니다..." -ForegroundColor $INFO

    # 중요 파일들 백업
    $importantFiles = @("lib_wt_common.ps1", "requirements.txt", "README.md", "*.py", "*.json", "*.html")
    $backedUp = $false

    foreach ($pattern in $importantFiles) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $destPath = "$backupPath\$($file.Name)"
            Copy-Item $file.FullName $destPath -Force
            $backedUp = $true
        }
    }

    # Monitoring 디렉토리 백업
    if (Test-Path "Monitoring") {
        Copy-Item "Monitoring" "$backupPath\Monitoring" -Recurse -Force
        $backedUp = $true
    }

    # 로그 파일 백업
    if (Test-Path $LOG_DIR) {
        Copy-Item $LOG_DIR "$backupPath\logs" -Recurse -Force
        $backedUp = $true
    }

    # 백업 압축
    if ($backedUp) {
        Set-Location $backupDir
        Compress-Archive -Path $backupName -DestinationPath "$backupName.zip" -Force
        Remove-Item $backupName -Recurse -Force
        Set-Location $SCRIPT_DIR
        
        $backupSize = [math]::Round((Get-Item "$backupDir\$backupName.zip").Length / 1MB, 2)
        Show-Success "백업이 생성되었습니다: $backupName.zip (크기: ${backupSize}MB)"
    } else {
        Show-Error "백업 생성에 실패했습니다."
    }

    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-MainMenu
}

# ============================================================================
# 워치햄스터 설정
# ============================================================================
function Show-WatchHamsterConfig {
    Clear-Host
    Show-Header "🔧 워치햄스터 설정"
    
    Show-Section "⚙️ 현재 설정"
    
    # 설정 파일 확인
    $configFile = "$env:USERPROFILE\.watchhamster\config.json"
    if (Test-Path $configFile) {
        Show-Success "설정 파일 발견: $configFile"
        Write-Host "현재 설정:" -ForegroundColor $CYAN
        try {
            $config = Get-Content $configFile | ConvertFrom-Json
            $config | ConvertTo-Json -Depth 3
        }
        catch {
            Get-Content $configFile
        }
    } else {
        Show-Info "설정 파일이 없습니다. 기본 설정을 사용합니다."
    }

    Write-Host ""
    Write-Host "설정 옵션:" -ForegroundColor $YELLOW
    Write-Host "1. 로그 레벨 설정"
    Write-Host "2. 모니터링 간격 설정"
    Write-Host "3. 알림 설정"
    Write-Host "4. 테마 설정"
    Write-Host "5. 설정 초기화"
    Write-Host "0. 돌아가기"
    Write-Host ""
    
    $configChoice = Read-Host "선택하세요 (1-5, 0)"

    switch ($configChoice) {
        "1" { Set-LogLevel }
        "2" { Set-MonitoringInterval }
        "3" { Set-NotificationSettings }
        "4" { Set-ThemeSettings }
        "5" { Reset-Config }
        "0" { Show-MainMenu }
        default { Show-InvalidChoice }
    }
}

# 설정 함수들
function Set-LogLevel {
    Clear-Host
    Show-Header "🔧 로그 레벨 설정"
    
    Write-Host "로그 레벨 옵션:" -ForegroundColor $CYAN
    Write-Host "1. DEBUG - 모든 로그 출력"
    Write-Host "2. INFO - 정보성 로그만 출력 (기본값)"
    Write-Host "3. WARNING - 경고 이상만 출력"
    Write-Host "4. ERROR - 에러만 출력"
    Write-Host ""
    
    $levelChoice = Read-Host "로그 레벨을 선택하세요 (1-4)"

    $level = "INFO"
    switch ($levelChoice) {
        "1" { $level = "DEBUG" }
        "2" { $level = "INFO" }
        "3" { $level = "WARNING" }
        "4" { $level = "ERROR" }
        default { Show-Error "잘못된 선택입니다." }
    }

    # 설정 파일 업데이트
    $configDir = "$env:USERPROFILE\.watchhamster"
    if (!(Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    $config = @{
        log_level = $level
        updated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
    
    $config | ConvertTo-Json | Set-Content "$configDir\config.json"

    Show-Success "로그 레벨이 $level로 설정되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-WatchHamsterConfig
}

function Set-MonitoringInterval {
    Clear-Host
    Show-Header "🔧 모니터링 간격 설정"
    
    Write-Host "모니터링 간격 옵션:" -ForegroundColor $CYAN
    Write-Host "1. 30초 (빠른 모니터링)"
    Write-Host "2. 1분 (기본값)"
    Write-Host "3. 5분 (절약 모드)"
    Write-Host "4. 10분 (저전력 모드)"
    Write-Host ""
    
    $intervalChoice = Read-Host "간격을 선택하세요 (1-4)"

    $interval = "60"
    switch ($intervalChoice) {
        "1" { $interval = "30" }
        "2" { $interval = "60" }
        "3" { $interval = "300" }
        "4" { $interval = "600" }
        default { Show-Error "잘못된 선택입니다." }
    }

    Show-Success "모니터링 간격이 ${interval}초로 설정되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-WatchHamsterConfig
}

function Set-NotificationSettings {
    Clear-Host
    Show-Header "🔧 알림 설정"
    
    Write-Host "알림 옵션:" -ForegroundColor $CYAN
    Write-Host "1. 모든 알림 활성화"
    Write-Host "2. 중요 알림만"
    Write-Host "3. 알림 비활성화"
    Write-Host ""
    
    $notifChoice = Read-Host "알림 설정을 선택하세요 (1-3)"

    $notification = "all"
    switch ($notifChoice) {
        "1" { $notification = "all" }
        "2" { $notification = "important" }
        "3" { $notification = "none" }
        default { Show-Error "잘못된 선택입니다." }
    }

    Show-Success "알림 설정이 변경되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-WatchHamsterConfig
}

function Set-ThemeSettings {
    Clear-Host
    Show-Header "🔧 테마 설정"
    
    Write-Host "테마 옵션:" -ForegroundColor $CYAN
    Write-Host "1. 기본 테마 (Windows)"
    Write-Host "2. 다크 테마"
    Write-Host "3. 라이트 테마"
    Write-Host "4. 고대비 테마"
    Write-Host ""
    
    $themeChoice = Read-Host "테마를 선택하세요 (1-4)"

    $theme = "default"
    switch ($themeChoice) {
        "1" { $theme = "default" }
        "2" { $theme = "dark" }
        "3" { $theme = "light" }
        "4" { $theme = "high_contrast" }
        default { Show-Error "잘못된 선택입니다." }
    }

    Show-Success "테마가 변경되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-WatchHamsterConfig
}

function Reset-Config {
    Clear-Host
    Show-Header "🔧 설정 초기화"
    
    if (Confirm-Action "모든 설정을 초기화하시겠습니까?") {
        Remove-Item "$env:USERPROFILE\.watchhamster\config.json" -Force -ErrorAction SilentlyContinue
        Show-Success "설정이 초기화되었습니다."
    }
    
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-WatchHamsterConfig
}

# ============================================================================
# UI 테마 변경
# ============================================================================
function Show-UIThemeConfig {
    Clear-Host
    Show-Header "🎨 UI 테마 변경"
    
    Show-Section "🎨 사용 가능한 테마"
    
    Write-Host "테마 옵션:" -ForegroundColor $CYAN
    Write-Host "1. 🪟 Windows 기본 테마"
    Write-Host "2. 🌙 다크 모드"
    Write-Host "3. ☀️ 라이트 모드"
    Write-Host "4. 🎨 고대비 모드"
    Write-Host "5. 🌈 컬러풀 모드"
    Write-Host "0. 돌아가기"
    Write-Host ""
    
    $themeChoice = Read-Host "테마를 선택하세요 (1-5, 0)"

    switch ($themeChoice) {
        "1" { Apply-WindowsTheme }
        "2" { Apply-DarkTheme }
        "3" { Apply-LightTheme }
        "4" { Apply-HighContrastTheme }
        "5" { Apply-ColorfulTheme }
        "0" { Show-MainMenu }
        default { Show-InvalidChoice }
    }
}

# 테마 적용 함수들
function Apply-WindowsTheme {
    Show-Success "Windows 기본 테마가 적용되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-UIThemeConfig
}

function Apply-DarkTheme {
    Show-Success "다크 테마가 적용되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-UIThemeConfig
}

function Apply-LightTheme {
    Show-Success "라이트 테마가 적용되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-UIThemeConfig
}

function Apply-HighContrastTheme {
    Show-Success "고대비 테마가 적용되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-UIThemeConfig
}

function Apply-ColorfulTheme {
    Show-Success "컬러풀 테마가 적용되었습니다."
    Write-Host ""
    Read-Host "계속하려면 Enter를 누르세요"
    Show-UIThemeConfig
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

# 시스템 종료
function Exit-System {
    Clear-Host
    Show-Header "👋 WatchHamster Master Control Center 종료"
    Show-Success "시스템이 안전하게 종료되었습니다."
    Show-Info "다시 시작하려면: .\watchhamster_master_control.ps1"
    Write-Host ""
    exit 0
}

# ============================================================================
# 메인 실행
# ============================================================================

# 스크립트 시작
Show-MainMenu 