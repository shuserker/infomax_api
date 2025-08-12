#!/bin/bash
# ============================================================================
# POSCO 메인 알림 시스템 직접 시작 (Mac용)
# ============================================================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
RESET='\033[0m'

# 스크립트 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "============================================================================"
echo -e "${CYAN}🏭 POSCO 메인 알림 시스템 직접 시작${RESET}"
echo "============================================================================"
echo

echo -e "${BLUE}📍 현재 경로: $(pwd)${RESET}"
echo

# 파일 존재 확인
if [[ -f "Monitoring/POSCO_News_250808/posco_main_notifier.py" ]]; then
    echo -e "${GREEN}✅ posco_main_notifier.py 파일 발견${RESET}"
else
    echo -e "${RED}❌ posco_main_notifier.py 파일을 찾을 수 없습니다.${RESET}"
    echo -e "${BLUE}📍 현재 경로: $(pwd)${RESET}"
    echo -e "${BLUE}📁 파일 목록:${RESET}"
    ls -la Monitoring/POSCO News 250808_mini/*.py 2>/dev/null || echo "Python 파일이 없습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${RESET}"
    echo -e "${YELLOW}💡 Python3를 설치한 후 다시 시도해주세요.${RESET}"
    echo
    read -p "계속하려면 Enter를 누르세요..."
    exit 1
fi

echo -e "${GREEN}✅ Python3 환경 확인됨${RESET}"
echo

echo -e "${CYAN}🚀 POSCO 메인 알림 시스템 시작 중...${RESET}"
echo -e "${YELLOW}🛑 종료하려면 Ctrl+C를 누르세요${RESET}"
echo

cd Monitoring/POSCO News 250808_mini
python3 Monitoring/POSCO_News_250808/posco_main_notifier.py

exit_code=$?

if [[ $exit_code -ne 0 ]]; then
    echo
    echo -e "${RED}❌ 시스템 실행에 실패했습니다. (오류 코드: $exit_code)${RESET}"
    echo -e "${YELLOW}💡 해결 방법:${RESET}"
    echo -e "${WHITE}   1. Python3가 설치되어 있는지 확인${RESET}"
    echo -e "${WHITE}   2. 필요한 패키지가 설치되어 있는지 확인 (pip3 install -r requirements.txt)${RESET}"
    echo -e "${WHITE}   3. config.py 파일의 설정 확인${RESET}"
    echo
    read -p "계속하려면 Enter를 누르세요..."
else
    echo
    echo -e "${GREEN}✅ 시스템이 정상적으로 종료되었습니다.${RESET}"
fi

cd ../..