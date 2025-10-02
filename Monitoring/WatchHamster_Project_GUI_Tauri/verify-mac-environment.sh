#!/bin/bash

# 🍎 맥 환경 검증 스크립트
# WatchHamster Tauri 프로젝트 맥 이전 후 검증

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

# 결과 저장 변수
RESULTS=()
OVERALL_STATUS="PASS"

# 테스트 결과 기록
record_result() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    RESULTS+=("$test_name:$status:$details")
    
    if [ "$status" = "FAIL" ]; then
        OVERALL_STATUS="FAIL"
    fi
}

echo "🍎 WatchHamster 맥 환경 검증을 시작합니다..."
echo "=================================================="

# 1. 시스템 정보 확인
log_info "시스템 정보 확인 중..."
MACOS_VERSION=$(sw_vers -productVersion)
ARCH=$(uname -m)
log_success "macOS $MACOS_VERSION ($ARCH)"

# 2. Node.js 확인
log_info "Node.js 확인 중..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -ge 20 ]; then
        log_success "Node.js $NODE_VERSION ✅"
        record_result "nodejs" "PASS" "$NODE_VERSION"
    else
        log_warning "Node.js $NODE_VERSION (권장: v20.19.0 이상)"
        record_result "nodejs" "WARNING" "$NODE_VERSION"
    fi
else
    log_error "Node.js가 설치되지 않았습니다"
    record_result "nodejs" "FAIL" "Not installed"
fi

# 3. Python 확인
log_info "Python 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "$PYTHON_VERSION ✅"
    record_result "python" "PASS" "$PYTHON_VERSION"
else
    log_error "Python3가 설치되지 않았습니다"
    record_result "python" "FAIL" "Not installed"
fi

# 4. 필수 도구 확인
log_info "필수 도구 확인 중..."

# Git 확인
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    log_success "$GIT_VERSION ✅"
    record_result "git" "PASS" "$GIT_VERSION"
else
    log_error "Git이 설치되지 않았습니다"
    record_result "git" "FAIL" "Not installed"
fi

# 5. 포트 사용 가능성 확인
log_info "포트 사용 가능성 확인 중..."

check_port() {
    local port=$1
    if lsof -i :$port &> /dev/null; then
        log_warning "포트 $port가 사용 중입니다"
        record_result "port_$port" "WARNING" "In use"
        return 1
    else
        log_success "포트 $port 사용 가능 ✅"
        record_result "port_$port" "PASS" "Available"
        return 0
    fi
}

check_port 1420  # 프론트엔드
check_port 8000  # 백엔드

# 6. 프로젝트 파일 확인
log_info "프로젝트 파일 확인 중..."

check_file() {
    local file=$1
    if [ -f "$file" ]; then
        log_success "$file 존재 ✅"
        record_result "file_$(basename $file)" "PASS" "Exists"
    else
        log_error "$file 파일이 없습니다"
        record_result "file_$(basename $file)" "FAIL" "Missing"
    fi
}

check_file "package.json"
check_file "vite.config.ts"
check_file "python-backend/main.py"
check_file "python-backend/requirements.txt"

# 7. 스크립트 실행 권한 확인
log_info "스크립트 실행 권한 확인 중..."

check_executable() {
    local script=$1
    if [ -x "$script" ]; then
        log_success "$script 실행 가능 ✅"
        record_result "executable_$(basename $script)" "PASS" "Executable"
    else
        log_warning "$script 실행 권한 없음 (chmod +x $script 실행 필요)"
        record_result "executable_$(basename $script)" "WARNING" "Not executable"
    fi
}

check_executable "setup.sh"
check_executable "run-dev.sh"
check_executable "stop.sh"

# 8. 의존성 설치 상태 확인
log_info "의존성 설치 상태 확인 중..."

if [ -d "node_modules" ]; then
    log_success "Node.js 의존성 설치됨 ✅"
    record_result "node_dependencies" "PASS" "Installed"
else
    log_warning "Node.js 의존성 미설치 (npm install 필요)"
    record_result "node_dependencies" "WARNING" "Not installed"
fi

if [ -f "python-backend/requirements.txt" ]; then
    # Python 가상환경 확인
    if [ -d "python-backend/venv" ]; then
        log_success "Python 가상환경 존재 ✅"
        record_result "python_venv" "PASS" "Exists"
    else
        log_warning "Python 가상환경 미생성"
        record_result "python_venv" "WARNING" "Not created"
    fi
fi

# 결과 요약
echo ""
echo "=================================================="
echo "🍎 맥 환경 검증 결과"
echo "=================================================="

for result in "${RESULTS[@]}"; do
    IFS=':' read -r test status details <<< "$result"
    case $status in
        "PASS")
            echo -e "${GREEN}✅ $test${NC}: $details"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $test${NC}: $details"
            ;;
        "FAIL")
            echo -e "${RED}❌ $test${NC}: $details"
            ;;
    esac
done

echo ""
echo "=================================================="
if [ "$OVERALL_STATUS" = "PASS" ]; then
    log_success "🎉 전체 검증 완료! 맥 환경에서 개발 가능합니다."
    echo ""
    echo "다음 단계:"
    echo "1. ./setup.sh 실행 (의존성 설치)"
    echo "2. ./run-dev.sh 실행 (개발 서버 시작)"
    echo "3. http://localhost:1420 접속"
else
    log_error "⚠️  일부 검증 실패. 위의 경고/오류를 해결해주세요."
    echo ""
    echo "해결 방법:"
    echo "1. Node.js 설치: brew install node"
    echo "2. Python 설치: brew install python"
    echo "3. 스크립트 권한: chmod +x *.sh"
fi

# JSON 결과 파일 생성
cat > mac-verification-results.json << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": "macOS $MACOS_VERSION ($ARCH)",
  "overall_status": "$OVERALL_STATUS",
  "results": [
$(printf '%s\n' "${RESULTS[@]}" | sed 's/\(.*\):\(.*\):\(.*\)/    {"test": "\1", "status": "\2", "details": "\3"}/' | paste -sd ',' -)
  ]
}
EOF

log_info "결과가 mac-verification-results.json에 저장되었습니다"

exit 0