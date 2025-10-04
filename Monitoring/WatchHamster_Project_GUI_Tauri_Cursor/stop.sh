#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 제목 출력
clear
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ⏹️  WatchHamster 중지                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

echo -e "${BLUE}🛑 WatchHamster 관련 프로세스를 중지합니다...${NC}"

# Node.js 프로세스 중지
echo -e "${BLUE}🔧 Node.js 프로세스 중지 중...${NC}"
if pkill -f "node.*vite" 2>/dev/null; then
    echo -e "${GREEN}✅ Node.js 프로세스 중지됨${NC}"
else
    echo -e "${YELLOW}ℹ️  실행 중인 Node.js 프로세스가 없습니다${NC}"
fi

# Python 프로세스 중지
echo -e "${BLUE}🐍 Python 프로세스 중지 중...${NC}"
if pkill -f "python.*main.py" 2>/dev/null; then
    echo -e "${GREEN}✅ Python 프로세스 중지됨${NC}"
else
    echo -e "${YELLOW}ℹ️  실행 중인 Python 프로세스가 없습니다${NC}"
fi

# 추가 정리
pkill -f "uvicorn" 2>/dev/null
pkill -f "fastapi" 2>/dev/null

# 포트 확인
echo -e "${BLUE}🔍 포트 사용 상태 확인 중...${NC}"

if lsof -i :1420 &> /dev/null; then
    echo -e "${YELLOW}⚠️  포트 1420이 여전히 사용 중입니다${NC}"
    echo "   다음 명령어로 강제 종료할 수 있습니다:"
    echo "   sudo lsof -ti:1420 | xargs kill -9"
else
    echo -e "${GREEN}✅ 포트 1420 해제됨${NC}"
fi

if lsof -i :8000 &> /dev/null; then
    echo -e "${YELLOW}⚠️  포트 8000이 여전히 사용 중입니다${NC}"
    echo "   다음 명령어로 강제 종료할 수 있습니다:"
    echo "   sudo lsof -ti:8000 | xargs kill -9"
else
    echo -e "${GREEN}✅ 포트 8000 해제됨${NC}"
fi

echo
echo -e "${GREEN}✅ WatchHamster가 중지되었습니다!${NC}"
echo

sleep 3