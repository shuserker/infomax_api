#!/bin/bash
# ============================================================================
# POSCO WatchHamster v2 Test Runner
# 종합적인 테스트 프레임워크 실행 스크립트
# ============================================================================

# 스크립트 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
RESET='\033[0m'

# 함수 정의
print_header() {
    echo -e "${CYAN}============================================================================${RESET}"
    echo -e "${CYAN}$1${RESET}"
    echo -e "${CYAN}============================================================================${RESET}"
}

print_info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

# 환경 확인
check_environment() {
    print_info "환경 확인 중..."
    
    # Python3 확인
    if ! command -v python3 &> /dev/null; then
        print_error "Python3가 설치되지 않았습니다."
        return 1
    fi
    print_success "Python3 발견: $(python3 --version)"
    
    # 필요한 Python 모듈 확인
    local required_modules=("psutil" "requests")
    for module in "${required_modules[@]}"; do
# BROKEN_REF:         if python3 -c "import $module" 2>/dev/null; then
            print_success "Python 모듈 확인: $module"
        else
            print_warning "Python 모듈 누락: $module (일부 테스트가 제한될 수 있습니다)"
        fi
    done
    
    # 테스트 스크립트 확인
# BROKEN_REF:     local test_scripts=("test_v2_integration.py" "test_process_lifecycle.py" "test_control_center_integration.py" "run_comprehensive_tests.py")
    for script in "${test_scripts[@]}"; do
        if [[ -f "$script" ]]; then
            print_success "테스트 스크립트 확인: $script"
        else
            print_error "테스트 스크립트 누락: $script"
            return 1
        fi
    done
    
    return 0
}

# 개별 테스트 실행
run_individual_test() {
    local test_name="$1"
    local test_script="$2"
    
    print_header "🧪 $test_name"
    
    if [[ ! -f "$test_script" ]]; then
        print_error "테스트 스크립트를 찾을 수 없습니다: $test_script"
        return 1
    fi
    
    print_info "테스트 실행 중: $test_script"
    
    # 테스트 실행
    if python3 "$test_script"; then
        print_success "$test_name 완료"
        return 0
    else
        print_error "$test_name 실패"
        return 1
    fi
}

# 종합 테스트 실행
run_comprehensive_tests() {
    print_header "🚀 POSCO WatchHamster v2 종합 테스트 실행"
    
    if [[ -f "run_comprehensive_tests.py" ]]; then
        python3 run_comprehensive_tests.py
        return $?
    else
        print_error "run_comprehensive_tests.py"
        return 1
    fi
}

# 테스트 결과 확인
check_test_results() {
    print_header "📊 테스트 결과 확인"
    
    if [[ -f "test_results.json" ]]; then
        print_success "test_results.json"
        
        # JSON 파일 크기 확인
        local file_size=$(stat -f%z "test_results.json" 2>/dev/null || stat -c%s "test_results.json" 2>/dev/null)
        print_info "결과 파일 크기: $file_size bytes"
        
        # 간단한 결과 요약 추출
        if command -v jq &> /dev/null; then
            print_info "테스트 세션 정보:"
            jq -r '.session_start, .session_end, .total_duration' test_results.json 2>/dev/null || true
        else
            print_info "jq가 설치되지 않아 JSON 파싱을 건너뜁니다."
        fi
    else
        print_warning "테스트 결과 파일이 없습니다. 테스트를 먼저 실행하세요."
    fi
}

# 로그 정리
cleanup_logs() {
    print_header "🧹 로그 정리"
    
# BROKEN_REF:     local log_files=("test_results.json" "*.log" "*.status")
    local cleaned_count=0
    
    for pattern in "${log_files[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                rm -f "$file"
                print_info "삭제됨: $file"
                ((cleaned_count++))
            fi
        done
    done
    
    if [[ $cleaned_count -gt 0 ]]; then
        print_success "$cleaned_count개 파일이 정리되었습니다."
    else
        print_info "정리할 파일이 없습니다."
    fi
}

# 도움말 표시
show_help() {
    print_header "📖 POSCO WatchHamster v2 테스트 러너 도움말"
    
    echo -e "${WHITE}사용법:${RESET}"
    echo -e "  $0 [옵션]"
    echo
    echo -e "${WHITE}옵션:${RESET}"
    echo -e "  ${GREEN}all${RESET}           모든 테스트 실행 (기본값)"
    echo -e "  ${GREEN}v2${RESET}            v2 통합 테스트만 실행"
    echo -e "  ${GREEN}lifecycle${RESET}     프로세스 생명주기 테스트만 실행"
    echo -e "  ${GREEN}control${RESET}       제어센터 통합 테스트만 실행"
    echo -e "  ${GREEN}check${RESET}         환경 확인만 실행"
    echo -e "  ${GREEN}results${RESET}       테스트 결과 확인"
    echo -e "  ${GREEN}cleanup${RESET}       로그 파일 정리"
    echo -e "  ${GREEN}help${RESET}          이 도움말 표시"
    echo
    echo -e "${WHITE}예시:${RESET}"
    echo -e "  $0                # 모든 테스트 실행"
    echo -e "  $0 v2             # v2 통합 테스트만 실행"
    echo -e "  $0 check          # 환경 확인"
    echo -e "  $0 cleanup        # 로그 정리"
}

# 메인 로직
main() {
    local command="${1:-all}"
    
    case "$command" in
        "all")
            if check_environment; then
                run_comprehensive_tests
            else
                print_error "환경 확인 실패. 테스트를 실행할 수 없습니다."
                exit 1
            fi
            ;;
        "v2")
            if check_environment; then
# BROKEN_REF:                 run_individual_test "v2 통합 테스트" "test_v2_integration.py"
            else
                exit 1
            fi
            ;;
        "lifecycle")
            if check_environment; then
                run_individual_test "프로세스 생명주기 테스트" "test_process_lifecycle.py"
            else
                exit 1
            fi
            ;;
        "control")
            if check_environment; then
                run_individual_test "제어센터 통합 테스트" "test_control_center_integration.py"
            else
                exit 1
            fi
            ;;
        "check")
            check_environment
            ;;
        "results")
            check_test_results
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "알 수 없는 명령: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"