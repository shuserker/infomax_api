#!/bin/bash
# POSCO WatchHamster v3.0.0 마이그레이션 롤백 스크립트

set -e  # 오류 시 중단

echo "🔄 POSCO WatchHamster v3.0 시작"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[단계 $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 백업 디렉토리 찾기
print_step "1" "백업 디렉토리 확인"

BACKUP_DIR=$(ls -1d backup_* 2>/dev/null | tail -1)

if [ -z "$BACKUP_DIR" ]; then
    print_error "백업 디렉토리를 찾을 수 없습니다."
    echo "사용 가능한 백업:"
    ls -1d backup_* 2>/dev/null || echo "백업 없음"
    exit 1
fi

print_success "백업 디렉토리 발견: $BACKUP_DIR"

# 현재 실행 중인 프로세스 중지
print_step "2" "현재 프로세스 중지"

if pgrep -f ".naming_backup/config_data_backup/watchhamster.log" > /dev/null; then
    print_warning "워치햄스터 중지 중..."
    pkill -f ".naming_backup/config_data_backup/watchhamster.log"
    sleep 5
fi

if pgrep -f "python.*posco" > /dev/null; then
    print_warning "POSCO 관련 프로세스 중지 중..."
    pkill -f "python.*posco"
    sleep 3
fi

print_success "프로세스 중지 완료"

# 백업에서 복원
print_step "3" "백업에서 시스템 복원"

# 현재 v2 시스템 백업 (롤백 전)
ROLLBACK_BACKUP="rollback_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ROLLBACK_BACKUP"
cp -r Monitoring/ "$ROLLBACK_BACKUP/" 2>/dev/null || true
cp watchhamster_control_center.sh "$ROLLBACK_BACKUP/" 2>/dev/null || true

print_success "롤백 전 현재 상태 백업: $ROLLBACK_BACKUP"

# 백업에서 복원
if [ -d "$BACKUP_DIR/Monitoring" ]; then
    rm -rf Monitoring/
    cp -r "$BACKUP_DIR/Monitoring" ./
    print_success "Monitoring 디렉토리 복원"
fi

if [ -f ".naming_backup/scripts/watchhamster_control_center.sh" ]; then
    cp ".naming_backup/scripts/watchhamster_control_center.sh" ./
    chmod +x watchhamster_control_center.sh
    print_success "워치햄스터 제어센터 스크립트 복원"
fi

# 로그 파일 복원 (선택적)
if ls "$BACKUP_DIR"/*.log 1> /dev/null 2>&1; then
    cp "$BACKUP_DIR"/*.log ./
    print_success "로그 파일 복원"
fi

# v2 디렉토리 제거
print_step "4" "v2 아키텍처 제거"

if [ -d "Monitoring/POSCO News 250808_mini_v2" ]; then
    rm -rf "Monitoring/POSCO News 250808_mini_v2"
    print_success "v2 아키텍처 디렉토리 제거"
fi

# 복원 검증
print_step "5" "복원 검증"

# 기존 워치햄스터 테스트
print_warning "기존 워치햄스터 테스트 시작 (10초간)..."
timeout 10s python3 Monitoring/POSCO News 250808_mini/monitor_WatchHamster.py &
TEST_PID=$!

sleep 5

if kill -0 $TEST_PID 2>/dev/null; then
    print_success "기존 워치햄스터 테스트 성공"
    kill $TEST_PID 2>/dev/null
    wait $TEST_PID 2>/dev/null || true
else
    print_error "기존 WatchHamster v3.0 실패"
fi

# 롤백 완료
print_step "6" "롤백 완료"

echo ""
echo "🔄 POSCO WatchHamster v3.0 마이그레이션 롤백 완료!"
echo ""
echo "📋 롤백 결과:"
echo "  ✅ 기존 시스템으로 복원"
echo "  ✅ v2 아키텍처 제거"
echo "  ✅ 백업에서 설정 복원"
echo ""
echo "📦 백업 정보:"
echo "  - 원본 백업: $BACKUP_DIR"
echo "  - 롤백 전 백업: $ROLLBACK_BACKUP"
echo ""
echo "🚀 다음 단계:"
echo "  1. ./watchhamster_control_center.sh 실행"
echo "  2. 기존 방식으로 시스템 시작"
echo ""
echo "💡 참고:"
echo "migrate_to_v2.sh"
# BROKEN_REF: echo "  - 문제 발생 시 로그 확인: tail -f *.log"
echo ""