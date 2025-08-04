# ============================================================================
# Windows PowerShell 워치햄스터 공통 라이브러리 v4.0
# Windows 10/11 PowerShell 최적화
# 모든 워치햄스터 PowerShell 스크립트에서 사용하는 공통 함수들
# ============================================================================

# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ============================================================================
# 현대적 색상 팔레트 (Windows 11 Fluent Design 기반)
# ============================================================================

# 기본 제어
$RESET = ""
$BOLD = ""
$DIM = ""
$UNDERLINE = ""

# Windows 11 Fluent Design 색상
$PRIMARY = "Blue"      # Windows Blue
$SECONDARY = "Green"   # Success Green  
$ACCENT = "Yellow"     # Warning Orange
$DANGER = "Red"        # Error Red

# 뉴트럴 색상 (고대비 지원)
$WHITE = "White"
$LIGHT_GRAY = "Gray"
$GRAY = "DarkGray"
$DARK_GRAY = "DarkGray"
$BLACK = "Black"

# 기능별 색상 (접근성 고려)
$SUCCESS = "Green"
$ERROR = "Red"
$WARNING = "Yellow"
$INFO = "Blue"

# 레거시 호환성 (기존 코드 지원)
$RED = $ERROR
$GREEN = $SUCCESS
$YELLOW = $WARNING
$BLUE = $INFO
$CYAN = $INFO
$MAGENTA = $ACCENT
$HEADER = $PRIMARY

# ============================================================================
# 로깅 시스템 (개선됨)
# ============================================================================

# 로그 파일 경로
$LOG_DIR = "$env:USERPROFILE\.watchhamster\logs"
$LOG_FILE = "$LOG_DIR\system.log"
$ERROR_LOG = "$LOG_DIR\error.log"

# 로그 디렉토리 생성
if (!(Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# 로그 함수들
function Write-LogMessage {
    param(
        [string]$Level,
        [string]$Message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LOG_FILE -Value $logEntry
}

function Write-LogInfo {
    param([string]$Message)
    Write-LogMessage "INFO" $Message
}

function Write-LogWarning {
    param([string]$Message)
    Write-LogMessage "WARNING" $Message
}

function Write-LogError {
    param([string]$Message)
    Write-LogMessage "ERROR" $Message
    Add-Content -Path $ERROR_LOG -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [ERROR] $Message"
}

function Write-LogSuccess {
    param([string]$Message)
    Write-LogMessage "SUCCESS" $Message
}

# ============================================================================
# 시스템 정보 함수들 (개선됨)
# ============================================================================

# 개선된 메모리 사용률 계산
function Get-MemoryUsage {
    try {
        $memory = Get-Counter "\Memory\Available MBytes"
        $totalMemory = (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1MB
        $availableMemory = $memory.CounterSamples[0].CookedValue
        $usedMemory = $totalMemory - $availableMemory
        $usagePercent = [math]::Round(($usedMemory / $totalMemory) * 100, 1)
        return $usagePercent
    }
    catch {
        return "N/A"
    }
}

# CPU 사용률
function Get-CpuUsage {
    try {
        $cpu = Get-Counter "\Processor(_Total)\% Processor Time"
        return [math]::Round($cpu.CounterSamples[0].CookedValue, 1)
    }
    catch {
        return "N/A"
    }
}

# 디스크 사용률
function Get-DiskUsage {
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
        return [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)
    }
    catch {
        return "N/A"
    }
}

# 시스템 정보 출력
function Show-SystemInfo {
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Gray
    Write-Host "║                           📊 시스템 정보                                    ║" -ForegroundColor Cyan
    Write-Host "╠═══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor Gray
    
    # CPU 정보
    $cpuUsage = Get-CpuUsage
    Write-Host "║  CPU 사용률: $cpuUsage%" -ForegroundColor White
    
    # 메모리 정보 (개선됨)
    $memUsage = Get-MemoryUsage
    Write-Host "║  메모리 사용률: $memUsage%" -ForegroundColor White
    
    # 디스크 정보
    $diskUsage = Get-DiskUsage
    Write-Host "║  디스크 사용률: $diskUsage%" -ForegroundColor White
    
    # Python 버전
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Host "║  Python 버전: $pythonVersion" -ForegroundColor White
        } else {
            Write-Host "║  Python 버전: N/A" -ForegroundColor White
        }
    }
    catch {
        Write-Host "║  Python 버전: N/A" -ForegroundColor White
    }
    
    # 네트워크 상태
    try {
        $ping = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
        if ($ping) {
            Write-Host "║  네트워크: 연결됨" -ForegroundColor Green
        } else {
            Write-Host "║  네트워크: 연결 안됨" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "║  네트워크: 연결 안됨" -ForegroundColor Red
    }
    
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================================
# 공통 함수들
# ============================================================================

# 함수: 헤더 출력
function Show-Header {
    param([string]$Title)
    Write-Host "████████████████████████████████████████████████████████████████████████████████" -ForegroundColor $HEADER
    Write-Host "██                                                                            ██" -ForegroundColor $HEADER
    Write-Host "██    $Title                                         ██" -ForegroundColor $HEADER
    Write-Host "██                                                                            ██" -ForegroundColor $HEADER
    Write-Host "████████████████████████████████████████████████████████████████████████████████" -ForegroundColor $HEADER
    Write-Host ""
    Write-LogInfo "Header displayed: $Title"
}

# 함수: 섹션 헤더 출력
function Show-Section {
    param([string]$Title)
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                           $Title                                    ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-LogInfo "Section displayed: $Title"
}

# 함수: 성공 메시지
function Show-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $SUCCESS
    Write-LogSuccess $Message
}

# 함수: 에러 메시지
function Show-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ERROR
    Write-LogError $Message
}

# 함수: 경고 메시지
function Show-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor $WARNING
    Write-LogWarning $Message
}

# 함수: 정보 메시지
function Show-Info {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor $INFO
    Write-LogInfo $Message
}

# 함수: 로딩 애니메이션
function Show-Loading {
    param([string]$Message)
    $spinner = @('⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏')
    $i = 0
    
    Write-Host "$Message " -NoNewline
    while ($true) {
        Write-Host "`b$($spinner[$i % $spinner.Length])" -NoNewline
        Start-Sleep -Milliseconds 100
        $i++
    }
}

# 함수: 박스 시작
function Start-Box {
    param([string]$Color)
    Write-Host "╔═══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Color
}

# 함수: 박스 끝
function End-Box {
    param([string]$Color)
    Write-Host "╚═══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Color
}

# 함수: 메뉴 아이템 출력
function Show-MenuItem {
    param([string]$Number, [string]$Title, [string]$Description)
    Write-Host "║  $Number $Title" -ForegroundColor White
    Write-Host "║     $Description" -ForegroundColor Gray
}

# 함수: Python 환경 확인
function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Show-Success "Python 발견: $pythonVersion"
            return $true
        } else {
            Show-Error "Python이 설치되지 않았습니다."
            Show-Info "Python을 설치해주세요: https://www.python.org/downloads/"
            return $false
        }
    }
    catch {
        Show-Error "Python이 설치되지 않았습니다."
        Show-Info "Python을 설치해주세요: https://www.python.org/downloads/"
        return $false
    }
}

# 함수: 필수 파일 확인
function Test-RequiredFiles {
    param([string[]]$Files)
    $missingFiles = @()
    
    foreach ($file in $Files) {
        if (!(Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -eq 0) {
        Show-Success "모든 필수 파일이 존재합니다."
        return $true
    } else {
        Show-Error "누락된 파일들:"
        foreach ($file in $missingFiles) {
            Write-Host "  • $file" -ForegroundColor Red
        }
        return $false
    }
}

# 함수: 네트워크 연결 확인
function Test-NetworkConnection {
    try {
        $ping = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
        if ($ping) {
            Show-Success "인터넷 연결이 정상입니다."
            return $true
        } else {
            Show-Error "인터넷 연결을 확인해주세요."
            return $false
        }
    }
    catch {
        Show-Error "인터넷 연결을 확인해주세요."
        return $false
    }
}

# 함수: Git 저장소 상태 확인
function Test-GitStatus {
    if (Test-Path ".git") {
        try {
            $status = git status --porcelain 2>$null
            if ([string]::IsNullOrEmpty($status)) {
                Show-Success "Git 저장소가 깨끗한 상태입니다."
            } else {
                Show-Warning "Git 저장소에 변경사항이 있습니다."
            }
            return $true
        }
        catch {
            Show-Warning "Git 저장소 상태를 확인할 수 없습니다."
            return $false
        }
    } else {
        Show-Warning "Git 저장소가 아닙니다."
        return $false
    }
}

# 함수: 프로세스 확인
function Test-Process {
    param([string]$ProcessName)
    $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
    if ($processes) {
        Show-Success "$ProcessName 프로세스가 실행 중입니다."
        return $true
    } else {
        Show-Info "$ProcessName 프로세스가 실행되지 않았습니다."
        return $false
    }
}

# 함수: 사용자 입력 처리
function Get-UserInput {
    param([string]$Prompt, [string]$Default = "")
    
    if ($Default) {
        $input = Read-Host "$Prompt (기본값: $Default)"
        if ([string]::IsNullOrEmpty($input)) {
            return $Default
        }
        return $input
    } else {
        return Read-Host $Prompt
    }
}

# 함수: 확인 대화상자
function Confirm-Action {
    param([string]$Message)
    $response = Read-Host "$Message (y/N)"
    return $response -match "^[yY](es)?$"
}

# 함수: 초기화
function Initialize-System {
    Write-LogInfo "시스템 초기화 시작"
    
    # 로그 디렉토리 생성
    if (!(Test-Path $LOG_DIR)) {
        New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
    }
    
    # Python 환경 확인
    Test-PythonEnvironment
    
    # 네트워크 연결 확인
    Test-NetworkConnection
    
    # Git 상태 확인
    Test-GitStatus
    
    Write-LogInfo "시스템 초기화 완료"
}

# 함수: 정리
function Cleanup-System {
    Write-LogInfo "시스템 정리 시작"
    # 필요한 정리 작업 수행
    Write-LogInfo "시스템 정리 완료"
}

# 스크립트 종료 시 정리
Register-EngineEvent PowerShell.Exiting -Action { Cleanup-System }

# 초기화 실행
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    Initialize-System
} 