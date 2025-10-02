#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 제목 출력
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  🚀 WatchHamster 시작                        ║"
echo "║                                                              ║"
echo "║  잠시만 기다려주세요... 서버를 시작하고 있습니다!              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# 이전 프로세스 정리
echo -e "${BLUE}🧹 이전 프로세스 정리 중...${NC}"
pkill -f "node.*vite" 2>/dev/null
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Node.js 확인
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되지 않았습니다!${NC}"
    echo "   ./setup.sh를 먼저 실행하세요."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# Python 확인
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python이 설치되지 않았습니다!${NC}"
    echo "   ./setup.sh를 먼저 실행하세요."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# node_modules 확인
if [ ! -d "node_modules" ]; then
    echo -e "${RED}❌ 패키지가 설치되지 않았습니다!${NC}"
    echo "   ./setup.sh를 먼저 실행하세요."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo -e "${GREEN}✅ 환경 확인 완료!${NC}"
echo

echo -e "${PURPLE}🌟 WatchHamster 개발 서버를 시작합니다...${NC}"
echo
echo -e "${YELLOW}┌─────────────────────────────────────────────────────────────┐${NC}"
echo -e "${YELLOW}│  💡 팁:                                                      │${NC}"
echo -e "${YELLOW}│  • 브라우저가 자동으로 열립니다                               │${NC}"
echo -e "${YELLOW}│  • 종료하려면 이 터미널에서 Ctrl+C를 누르세요                 │${NC}"
echo -e "${YELLOW}│  • 문제가 생기면 이 터미널의 메시지를 확인하세요               │${NC}"
echo -e "${YELLOW}└─────────────────────────────────────────────────────────────┘${NC}"
echo

# 개발 서버 시작
echo -e "${BLUE}🚀 서버 시작 중... (최대 30초 소요)${NC}"
echo

# 트랩 설정 (Ctrl+C 처리)
trap 'echo -e "\n${YELLOW}🛑 서버를 중지합니다...${NC}"; pkill -f "node.*vite"; pkill -f "python.*main.py"; exit 0' INT

npm run dev

# 오류 발생 시
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}❌ 서버 시작에 실패했습니다!${NC}"
    echo
    echo -e "${YELLOW}🔧 해결 방법:${NC}"
    echo "1. ./setup.sh를 다시 실행해보세요"
    echo "2. 컴퓨터를 재시작해보세요"
    echo "3. 포트 8000, 1420이 다른 프로그램에서 사용 중인지 확인하세요:"
    echo "   lsof -i :8000"
    echo "   lsof -i :1420"
    echo
    read -p "계속하려면 Enter를 누르세요..."
fi