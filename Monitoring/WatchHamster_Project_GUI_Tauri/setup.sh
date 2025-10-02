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
echo "║                    🚀 WatchHamster 설치                      ║"
echo "║                                                              ║"
echo "║  이 스크립트가 자동으로 모든 것을 설치해드립니다!              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# Node.js 확인
echo -e "${BLUE}🔍 Node.js 확인 중...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js 설치됨: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js가 설치되지 않았습니다!${NC}"
    echo "   https://nodejs.org 에서 다운로드하세요."
    echo "   또는 다음 명령어로 설치하세요:"
    echo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew install node"
    else
        echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
        echo "   sudo apt-get install -y nodejs"
    fi
    echo
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# Python 확인
echo -e "${BLUE}🔍 Python 확인 중...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python 설치됨: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python 설치됨: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python이 설치되지 않았습니다!${NC}"
    echo "   https://python.org 에서 다운로드하세요."
    echo "   또는 다음 명령어로 설치하세요:"
    echo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew install python"
    else
        echo "   sudo apt-get update"
        echo "   sudo apt-get install python3 python3-pip"
    fi
    echo
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo
echo -e "${PURPLE}📦 패키지 설치를 시작합니다...${NC}"
echo "   (처음 설치 시 2-3분 정도 걸릴 수 있습니다)"
echo

# Node.js 패키지 설치
echo -e "${BLUE}🔧 Node.js 패키지 설치 중...${NC}"
if npm install; then
    echo -e "${GREEN}✅ Node.js 패키지 설치 완료!${NC}"
else
    echo -e "${RED}❌ Node.js 패키지 설치 실패!${NC}"
    echo "   인터넷 연결을 확인하고 다시 시도해보세요."
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# Python 패키지 설치
echo -e "${BLUE}🐍 Python 패키지 설치 중...${NC}"
cd python-backend
if $PYTHON_CMD -m pip install -r requirements.txt; then
    echo -e "${GREEN}✅ Python 패키지 설치 완료!${NC}"
else
    echo -e "${RED}❌ Python 패키지 설치 실패!${NC}"
    echo "   pip를 업데이트하고 다시 시도해보세요:"
    echo "   $PYTHON_CMD -m pip install --upgrade pip"
    cd ..
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi
cd ..

# 백엔드 테스트
echo -e "${BLUE}🧪 백엔드 테스트 중...${NC}"
cd python-backend
if $PYTHON_CMD test_backend.py &> /dev/null; then
    echo -e "${GREEN}✅ 백엔드 테스트 통과!${NC}"
else
    echo -e "${YELLOW}⚠️  백엔드 테스트에서 경고가 있지만 계속 진행합니다.${NC}"
fi
cd ..

echo
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 설치 완료!                             ║"
echo "║                                                              ║"
echo "║  이제 ./run-dev.sh 파일을 실행하여 WatchHamster를 시작하세요! ║"
echo "║                                                              ║"
echo "║  또는 터미널에서 'npm run dev' 명령어를 실행하세요.           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

echo -e "${CYAN}🌐 실행 후 접속 주소: http://localhost:1420${NC}"
echo -e "${CYAN}📚 사용법: QUICK_START.md 파일을 참고하세요${NC}"
echo

# 실행 권한 부여
chmod +x run-dev.sh
chmod +x stop.sh

echo -e "${GREEN}✅ 스크립트 실행 권한이 설정되었습니다.${NC}"
echo

read -p "계속하려면 Enter를 누르세요..."