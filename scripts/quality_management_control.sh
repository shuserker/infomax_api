#!/bin/bash
# POSCO 시스템 지속적 품질 관리 제어 스크립트
# Quality Management Control Script

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 헤더 출력
print_header() {
    echo "=================================================================="
    echo "🎯 POSCO 시스템 지속적 품질 관리 제어 센터"
    echo "   Continuous Quality Management Control Center"
    echo "=================================================================="
    echo ""
}

# 도움말 출력
show_help() {
    echo "사용법: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "명령어:"
    echo "  start-monitor [DURATION]  - 지속적 모니터링 시작 (기본: 3600초)"
    echo "  run-pipeline             - CI/CD 파이프라인 실행"
    echo "  generate-dashboard       - 품질 대시보드 생성"
    echo "  generate-report          - 품질 보고서 생성"
    echo "  run-tests               - 품질 관리 시스템 테스트 실행"
    echo "  status                  - 현재 시스템 상태 확인"
    echo "  install-deps            - 필요한 의존성 설치"
    echo "  help                    - 이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 start-monitor 1800    # 30분간 모니터링"
    echo "  $0 run-pipeline          # 파이프라인 실행"
    echo "  $0 generate-dashboard    # 대시보드 생성"
    echo ""
}

# 의존성 확인
check_dependencies() {
    log_info "의존성 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되어 있지 않습니다."
        return 1
    fi
    
    # 필수 Python 패키지 확인
    local required_packages=("psutil" "yaml" "schedule")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        log_warning "누락된 패키지: ${missing_packages[*]}"
        log_info "다음 명령으로 설치하세요: $0 install-deps"
        return 1
    fi
    
    log_success "모든 의존성이 설치되어 있습니다."
    return 0
}

# 의존성 설치
install_dependencies() {
    log_info "필요한 의존성 설치 중..."
    
    # pip 업그레이드
    python3 -m pip install --upgrade pip
    
    # 필수 패키지 설치
    python3 -m pip install psutil pyyaml schedule
    
    log_success "의존성 설치 완료"
}

# 모니터링 시작
start_monitoring() {
    local duration=${1:-3600}
    
    log_info "지속적 모니터링 시작 (지속 시간: ${duration}초)"
    
    if ! check_dependencies; then
        log_error "의존성 확인 실패"
        return 1
    fi
    
    python3 start_quality_management.py --mode monitor --duration "$duration" --verbose
}

# 파이프라인 실행
run_pipeline() {
    log_info "CI/CD 파이프라인 실행"
    
    if ! check_dependencies; then
        log_error "의존성 확인 실패"
        return 1
    fi
    
    python3 start_quality_management.py --mode pipeline --verbose
}

# 대시보드 생성
generate_dashboard() {
    log_info "품질 대시보드 생성"
    
    if ! check_dependencies; then
        log_error "의존성 확인 실패"
        return 1
    fi
    
    python3 start_quality_management.py --mode dashboard --verbose
}

# 보고서 생성
generate_report() {
    log_info "품질 보고서 생성"
    
    if ! check_dependencies; then
        log_error "의존성 확인 실패"
        return 1
    fi
    
    python3 start_quality_management.py --mode report --verbose
}

# 테스트 실행
run_tests() {
    log_info "품질 관리 시스템 테스트 실행"
    
    if ! check_dependencies; then
        log_error "의존성 확인 실패"
        return 1
    fi
    
    if [ -f "test_continuous_quality_management.py" ]; then
        python3 test_continuous_quality_management.py
    else
        log_error "테스트 파일을 찾을 수 없습니다: test_continuous_quality_management.py"
        return 1
    fi
}

# 시스템 상태 확인
check_status() {
    log_info "시스템 상태 확인"
    
    echo "📊 시스템 리소스:"
    echo "  - CPU 사용률: $(python3 -c "import psutil; print(f'{psutil.cpu_percent(interval=1):.1f}%')")"
    echo "  - 메모리 사용률: $(python3 -c "import psutil; print(f'{psutil.virtual_memory().percent:.1f}%')")"
    echo "  - 디스크 사용률: $(python3 -c "import psutil; print(f'{psutil.disk_usage(\".\").percent:.1f}%')")"
    
    echo ""
    echo "📁 중요 파일 존재 여부:"
    local critical_files=(
        "continuous_quality_management_system.py"
        "start_quality_management.py"
        "ci_config.yaml"
        "test_continuous_quality_management.py"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file (누락)"
        fi
    done
    
    echo ""
    echo "🐍 Python 환경:"
    echo "  - Python 버전: $(python3 --version)"
    echo "  - 현재 디렉토리: $(pwd)"
    
    # 최근 로그 파일 확인
    if [ -f "quality_management.log" ]; then
        echo ""
        echo "📋 최근 로그 (마지막 10줄):"
        tail -n 10 quality_management.log
    fi
}

# 메인 로직
main() {
    print_header
    
    case "${1:-help}" in
        "start-monitor")
            start_monitoring "$2"
            ;;
        "run-pipeline")
            run_pipeline
            ;;
        "generate-dashboard")
            generate_dashboard
            ;;
        "generate-report")
            generate_report
            ;;
        "run-tests")
            run_tests
            ;;
        "status")
            check_status
            ;;
        "install-deps")
            install_dependencies
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "알 수 없는 명령어: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"