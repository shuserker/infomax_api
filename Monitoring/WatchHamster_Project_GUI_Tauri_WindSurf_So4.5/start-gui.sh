#!/bin/bash
# WatchHamster GUI 시작 스크립트

echo "🐹 WatchHamster GUI 시작 중..."
echo ""

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📁 작업 디렉토리: $SCRIPT_DIR${NC}"
echo ""

# Node 모듈 확인
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules가 없습니다. 의존성을 설치합니다...${NC}"
    npm install
    echo ""
fi

# Python 백엔드 시작
echo -e "${GREEN}🐍 Python 백엔드 시작 중...${NC}"
cd python-backend
python3 main.py &
BACKEND_PID=$!
cd ..

# 백엔드가 준비될 때까지 대기
echo -e "${BLUE}⏳ 백엔드 준비 중... (5초)${NC}"
sleep 5

# 프론트엔드 시작
echo -e "${GREEN}⚛️  React 프론트엔드 시작 중...${NC}"
echo ""
echo -e "${GREEN}✅ GUI가 시작되었습니다!${NC}"
echo ""
echo -e "${BLUE}📊 접속 정보:${NC}"
echo -e "   🏠 메인 화면: ${GREEN}http://localhost:1420${NC}"
echo -e "   📚 API 문서: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}💡 종료하려면 Ctrl+C를 누르세요${NC}"
echo ""

# 프론트엔드 실행
npm run dev:frontend

# 종료 시 백엔드도 함께 종료
trap "echo ''; echo '🛑 서버를 종료합니다...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

wait
