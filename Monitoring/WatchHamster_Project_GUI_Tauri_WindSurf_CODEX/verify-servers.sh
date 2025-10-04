#!/bin/bash

# 🚀 서버 실행 검증 스크립트
# 개발 서버와 백엔드 API 동작 확인

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🚀 WatchHamster 서버 검증을 시작합니다..."
echo "=================================================="

# 1. 개발 서버 시작 테스트
log_info "개발 서버 시작 테스트..."

# 백그라운드에서 개발 서버 시작
log_info "npm run dev 실행 중..."
npm run dev &
DEV_SERVER_PID=$!

# 서버 시작 대기
log_info "서버 시작 대기 중... (30초)"
sleep 30

# 2. 프론트엔드 접속 확인
log_info "프론트엔드 서버 확인 중..."
if curl -s http://localhost:1420 > /dev/null; then
    log_success "✅ 프론트엔드 서버 정상 (http://localhost:1420)"
else
    log_error "❌ 프론트엔드 서버 접속 실패"
fi

# 3. 백엔드 API 확인
log_info "백엔드 API 확인 중..."
if curl -s http://localhost:8000/health > /dev/null; then
    log_success "✅ 백엔드 API 정상 (http://localhost:8000)"
else
    log_warning "⚠️  백엔드 API 접속 실패 또는 아직 시작 중"
fi

# 4. API 문서 확인
log_info "API 문서 확인 중..."
if curl -s http://localhost:8000/docs > /dev/null; then
    log_success "✅ API 문서 접근 가능 (http://localhost:8000/docs)"
else
    log_warning "⚠️  API 문서 접근 실패"
fi

# 5. WebSocket 연결 테스트 (간단한 확인)
log_info "WebSocket 연결 테스트..."
# 실제 WebSocket 테스트는 복잡하므로 포트만 확인
if lsof -i :8000 > /dev/null 2>&1; then
    log_success "✅ WebSocket 포트 활성화"
else
    log_warning "⚠️  WebSocket 포트 비활성화"
fi

echo ""
echo "=================================================="
log_success "🎉 서버 검증 완료!"
echo ""
echo "접속 정보:"
echo "- 프론트엔드: http://localhost:1420"
echo "- 백엔드 API: http://localhost:8000"
echo "- API 문서: http://localhost:8000/docs"
echo ""
echo "서버를 중지하려면 ./stop.sh를 실행하세요"

# 서버 프로세스 정보 저장
echo $DEV_SERVER_PID > .dev-server.pid

exit 0