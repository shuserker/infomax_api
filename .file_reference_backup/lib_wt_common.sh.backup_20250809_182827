#!/bin/bash
# ============================================================================
# Mac용 워치햄스터 공통 라이브러리 v4.0
# macOS 최적화 및 개선사항 반영
# 모든 워치햄스터 스크립트에서 사용하는 공통 함수들
# ============================================================================

# UTF-8 인코딩 설정
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# ============================================================================
# 현대적 색상 팔레트 (macOS Terminal 최적화)
# ============================================================================

# 기본 제어
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
UNDERLINE='\033[4m'

# macOS 시스템 색상 (RGB 기반)
PRIMARY='\033[38;2;0;122;255m'      # macOS Blue
SECONDARY='\033[38;2;52;199;89m'    # Success Green  
ACCENT='\033[38;2;255;149;0m'       # Warning Orange
DANGER='\033[38;2;255;59;48m'       # Error Red

# 뉴트럴 색상 (고대비 지원)
WHITE='\033[38;2;255;255;255m'
LIGHT_GRAY='\033[38;2;200;200;200m'
GRAY='\033[38;2;150;150;150m'
DARK_GRAY='\033[38;2;100;100;100m'
BLACK='\033[38;2;0;0;0m'

# 기능별 색상 (접근성 고려)
SUCCESS='\033[38;2;52;199;89m'
ERROR='\033[38;2;255;59;48m'
WARNING='\033[38;2;255;149;0m'
INFO='\033[38;2;0;122;255m'

# 배경 강조 (선택적 사용)
BG_PRIMARY='\033[48;2;0;122;255m'
BG_SUCCESS='\033[48;2;52;199;89m'
BG_WARNING='\033[48;2;255;149;0m'
BG_ERROR='\033[48;2;255;59;48m'

# 레거시 호환성 (기존 코드 지원)
RED=$ERROR
GREEN=$SUCCESS
YELLOW=$WARNING
BLUE=$INFO
CYAN=$INFO
MAGENTA=$ACCENT
HEADER="${PRIMARY}${BOLD}"

# ============================================================================
# 로깅 시스템 (개선됨)
# ============================================================================

# 로그 파일 경로
LOG_DIR="$HOME/.watchhamster/logs"
LOG_FILE="$LOG_DIR/system.log"
ERROR_LOG="$LOG_DIR/error.log"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 로그 함수들
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

log_info() {
    log_message "INFO" "$1"
}

log_warning() {
    log_message "WARNING" "$1"
}

log_error() {
    log_message "ERROR" "$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$ERROR_LOG"
}

log_success() {
    log_message "SUCCESS" "$1"
}

# ============================================================================
# 시스템 정보 함수들 (개선됨)
# ============================================================================

# 개선된 메모리 사용률 계산
get_memory_usage() {
    local total_mem=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024}')
    local free_mem=$(vm_stat 2>/dev/null | awk '/free/ {gsub(/\./, "", $3); print $3*4096/1024/1024/1024}')
    
    if [[ -n "$total_mem" && -n "$free_mem" ]]; then
        local used_mem=$(echo "$total_mem - $free_mem" | bc -l 2>/dev/null)
        local usage_percent=$(echo "scale=1; ($used_mem / $total_mem) * 100" | bc -l 2>/dev/null)
        echo "${usage_percent:-0}"
    else
        # 대체 방법: top 명령어 사용
        top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/[^0-9.]//g'
    fi
}

# CPU 사용률
get_cpu_usage() {
    top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//'
}

# 디스크 사용률
get_disk_usage() {
    df -h / | awk 'NR==2 {print $5}' | sed 's/%//'
}

# 시스템 정보 출력
print_system_info() {
    echo -e "${GRAY}╔═══════════════════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${GRAY}║${RESET}                           ${CYAN}📊 시스템 정보${RESET}                                    ${GRAY}║${RESET}"
    echo -e "${GRAY}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    
    # CPU 정보
    local cpu_usage=$(get_cpu_usage)
    echo -e "${GRAY}║${RESET}  ${WHITE}CPU 사용률:${RESET} ${cpu_usage:-N/A}%"
    
    # 메모리 정보 (개선됨)
    local mem_usage=$(get_memory_usage)
    echo -e "${GRAY}║${RESET}  ${WHITE}메모리 사용률:${RESET} ${mem_usage:-N/A}%"
    
    # 디스크 정보
    local disk_usage=$(get_disk_usage)
    echo -e "${GRAY}║${RESET}  ${WHITE}디스크 사용률:${RESET} ${disk_usage:-N/A}%"
    
    # Python 버전
    local python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
    echo -e "${GRAY}║${RESET}  ${WHITE}Python 버전:${RESET} ${python_version:-N/A}"
    
    # 네트워크 상태
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo -e "${GRAY}║${RESET}  ${WHITE}네트워크:${RESET} ${GREEN}연결됨${RESET}"
    else
        echo -e "${GRAY}║${RESET}  ${WHITE}네트워크:${RESET} ${RED}연결 안됨${RESET}"
    fi
    
    echo -e "${GRAY}╚═══════════════════════════════════════════════════════════════════════════════╝${RESET}"
    echo
}

# ============================================================================
# 공통 함수들
# ============================================================================

# 함수: 헤더 출력
print_header() {
    echo -e "${HEADER}████████████████████████████████████████████████████████████████████████████████${RESET}"
    echo -e "${HEADER}██                                                                            ██${RESET}"
    echo -e "${HEADER}██    $1                                         ██${RESET}"
    echo -e "${HEADER}██                                                                            ██${RESET}"
    echo -e "${HEADER}████████████████████████████████████████████████████████████████████████████████${RESET}"
    echo
    log_info "Header displayed: $1"
}

# 함수: 섹션 헤더 출력
print_section() {
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}║${RESET}                           $1                                    ${CYAN}║${RESET}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝${RESET}"
    echo
    log_info "Section displayed: $1"
}

# 함수: 성공 메시지
print_success() {
    echo -e "${SUCCESS}✅ $1${RESET}"
    log_success "$1"
}

# 함수: 에러 메시지
print_error() {
    echo -e "${ERROR}❌ $1${RESET}"
    log_error "$1"
}

# 함수: 경고 메시지
print_warning() {
    echo -e "${WARNING}⚠️ $1${RESET}"
    log_warning "$1"
}

# 함수: 정보 메시지
print_info() {
    echo -e "${INFO}ℹ️ $1${RESET}"
    log_info "$1"
}

# 함수: 로딩 애니메이션
show_loading() {
    local message="$1"
    local delay=0.1
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    
    echo -n "$message "
    while true; do
        printf "\b${spin:$((i % ${#spin})):1}"
        sleep $delay
        ((i++))
    done &
    local pid=$!
    
    # 함수 종료 시 애니메이션 중지
    trap "kill $pid 2>/dev/null" EXIT
    return $pid
}

# 함수: 로딩 중지
stop_loading() {
    local pid=$1
    kill $pid 2>/dev/null
    echo
}

# 함수: 박스 시작
start_box() {
    local color="$1"
    echo -e "${color}╔═══════════════════════════════════════════════════════════════════════════════╗${RESET}"
}

# 함수: 박스 끝
end_box() {
    local color="$1"
    echo -e "${color}╚═══════════════════════════════════════════════════════════════════════════════╝${RESET}"
}

# 함수: 메뉴 아이템 출력
print_menu_item() {
    local number="$1"
    local title="$2"
    local description="$3"
    echo -e "${GRAY}║${RESET}  ${YELLOW}$number${RESET} ${WHITE}$title${RESET}"
    echo -e "${GRAY}║${RESET}     ${GRAY}$description${RESET}"
}

# 함수: Python 환경 확인
check_python_environment() {
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python3 발견: $version"
        return 0
    elif command -v python &> /dev/null; then
        local version=$(python --version 2>&1 | cut -d' ' -f2)
        print_success "Python 발견: $version"
        return 0
    else
        print_error "Python이 설치되지 않았습니다."
        print_info "Python을 설치해주세요: https://www.python.org/downloads/"
        return 1
    fi
}

# 함수: 필수 파일 확인
check_required_files() {
    local files=("$@")
    local missing_files=()
    
    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        print_success "모든 필수 파일이 존재합니다."
        return 0
    else
        print_error "누락된 파일들:"
        for file in "${missing_files[@]}"; do
            echo -e "  ${RED}• $file${RESET}"
        done
        return 1
    fi
}

# 함수: 네트워크 연결 확인
check_network_connection() {
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        print_success "인터넷 연결이 정상입니다."
        return 0
    else
        print_error "인터넷 연결을 확인해주세요."
        return 1
    fi
}

# 함수: Git 저장소 상태 확인
check_git_status() {
    if [[ -d ".git" ]]; then
        local status=$(git status --porcelain 2>/dev/null)
        if [[ -z "$status" ]]; then
            print_success "Git 저장소가 깨끗한 상태입니다."
        else
            print_warning "Git 저장소에 변경사항이 있습니다."
        fi
        return 0
    else
        print_warning "Git 저장소가 아닙니다."
        return 1
    fi
}

# 함수: 프로세스 확인
check_process() {
    local process_name="$1"
    if pgrep -f "$process_name" >/dev/null; then
        print_success "$process_name 프로세스가 실행 중입니다."
        return 0
    else
        print_info "$process_name 프로세스가 실행되지 않았습니다."
        return 1
    fi
}

# 함수: 사용자 입력 처리
get_user_input() {
    local prompt="$1"
    local default="$2"
    
    if [[ -n "$default" ]]; then
        echo -n -e "${GREEN}$prompt${RESET} (기본값: $default): "
    else
        echo -n -e "${GREEN}$prompt${RESET}: "
    fi
    
    read -r user_input
    
    if [[ -z "$user_input" && -n "$default" ]]; then
        echo "$default"
    else
        echo "$user_input"
    fi
}

# 함수: 확인 대화상자
confirm_action() {
    local message="$1"
    echo -n -e "${YELLOW}$message${RESET} (y/N): "
    read -r response
    
    case "$response" in
        [yY]|[yY][eE][sS])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 함수: 초기화
init_system() {
    log_info "시스템 초기화 시작"
    
    # 로그 디렉토리 생성
    mkdir -p "$LOG_DIR"
    
    # Python 환경 확인
    check_python_environment
    
    # 네트워크 연결 확인
    check_network_connection
    
    # Git 상태 확인
    check_git_status
    
    log_info "시스템 초기화 완료"
}

# 함수: 정리
cleanup() {
    log_info "시스템 정리 시작"
    # 필요한 정리 작업 수행
    log_info "시스템 정리 완료"
}

# 스크립트 종료 시 정리
trap cleanup EXIT

# 초기화 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_system
fi 