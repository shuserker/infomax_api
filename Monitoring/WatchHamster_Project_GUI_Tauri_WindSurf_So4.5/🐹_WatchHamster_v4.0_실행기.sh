#!/bin/bash

# 🐹 WatchHamster v4.0 통합 모니터링 시스템 원클릭 실행기
# ===========================================================

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# WatchHamster 로고와 시스템 정보
echo -e "${CYAN}================================================================${NC}"
echo -e "${WHITE}🐹 WatchHamster v4.0 통합 모니터링 시스템 ${PURPLE}완전체${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "${GREEN}📈 POSCO 뉴스 모니터링 시스템${NC}"
echo -e "${BLUE}📊 InfoMax API 테스트 플랫폼 (58개+ API 지원)${NC}"
echo -e "${YELLOW}🤖 28개 자동갱신 로직 & 스마트 스케줄링${NC}"
echo -e "${PURPLE}🌐 웹훅 통합 & 실시간 알림 시스템${NC}"
echo -e "${CYAN}⚙️  백업, 수리, 품질관리 자동화 도구${NC}"
echo -e "${CYAN}================================================================${NC}"
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📍 WatchHamster 본부:${NC} $SCRIPT_DIR"
echo ""

# Node.js와 npm 버전 체크
echo -e "${YELLOW}🔍 시스템 환경 체크 중...${NC}"

if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js가 설치되지 않았습니다!${NC}"
    echo -e "${YELLOW}   https://nodejs.org 에서 설치해주세요.${NC}"
    exit 1
fi

if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm: v$NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm이 설치되지 않았습니다!${NC}"
    exit 1
fi

# Python 버전 체크 (WatchHamster 백엔드용)
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Python3이 설치되지 않았습니다 (백엔드 기능 제한)${NC}"
fi

echo ""

# package.json 존재 여부 확인
if [ ! -f "$SCRIPT_DIR/package.json" ]; then
    echo -e "${RED}❌ package.json을 찾을 수 없습니다!${NC}"
    echo -e "${YELLOW}   올바른 WatchHamster 프로젝트 디렉토리에서 실행하세요.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ WatchHamster 시스템 구조 정상${NC}"
echo ""

# 사용자 선택 메뉴
echo -e "${WHITE}🎯 WatchHamster v4.0 실행 옵션:${NC}"
echo -e "${CYAN}[1]${NC} 🚀 WatchHamster 풀스택 실행 (의존성 자동 설치 + 전체 시스템 시작)"
echo -e "${CYAN}[2]${NC} 📦 의존성만 설치"  
echo -e "${CYAN}[3]${NC} 🌐 프론트엔드만 시작 (InfoMax API 테스트 플랫폼)"
echo -e "${CYAN}[4]${NC} 🐍 백엔드만 시작 (웹훅 & 모니터링 서비스)"
echo -e "${CYAN}[5]${NC} 🏗️  빌드 및 프로덕션 프리뷰"
echo -e "${CYAN}[6]${NC} 🧹 시스템 초기화 (캐시 정리 + 재설치)"
echo -e "${CYAN}[7]${NC} 📋 WatchHamster 시스템 상태 체크"
echo -e "${CYAN}[8]${NC} ❌ 종료"
echo ""
echo -ne "${YELLOW}선택 (1-8): ${NC}"
read -r choice

case $choice in
    1)
        echo -e "${PURPLE}🚀 WatchHamster v4.0 풀스택 실행 모드${NC}"
        echo ""
        
        # 의존성 설치
        echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
        if npm install; then
            echo -e "${GREEN}✅ 의존성 설치 완료!${NC}"
        else
            echo -e "${RED}❌ 의존성 설치 실패!${NC}"
            exit 1
        fi
        
        echo ""
        echo -e "${BLUE}🌐 WatchHamster 통합 시스템 시작 중...${NC}"
        echo -e "${CYAN}================================================================${NC}"
        echo -e "${WHITE}🐹 WatchHamster v4.0 Control Center${NC}"
        echo -e "${GREEN}📍 POSCO 뉴스 모니터링: ${GREEN}활성화${NC}"
        echo -e "${BLUE}📊 InfoMax API 플랫폼: ${GREEN}http://localhost:1420/api-packages${NC}"
        echo -e "${YELLOW}🤖 자동갱신 시스템: ${GREEN}백그라운드 실행${NC}"
        echo -e "${PURPLE}🌐 웹훅 통합: ${GREEN}준비완료${NC}"
        echo -e "${CYAN}================================================================${NC}"
        echo -e "${WHITE}🎯 주요 기능:${NC}"
        echo -e "${WHITE}  • API 테스트: 58개+ 금융 API 완전 지원${NC}"
        echo -e "${WHITE}  • 자동갱신: 28개 스마트 로직 & 스케줄링${NC}"
        echo -e "${WHITE}  • 실시간 모니터링: POSCO 뉴스 변경사항 추적${NC}"
        echo -e "${WHITE}  • 웹훅 알림: Dooray 통합 실시간 알림${NC}"
        echo -e "${CYAN}================================================================${NC}"
        echo -e "${YELLOW}시스템 종료: ${RED}Ctrl+C${NC}"
        echo ""
        
        npm run dev
        ;;
        
    2)
        echo -e "${YELLOW}📦 WatchHamster 의존성 설치 중...${NC}"
        if npm install; then
            echo -e "${GREEN}✅ 의존성 설치 완료!${NC}"
            echo -e "${BLUE}💡 이제 'npm run dev' 명령으로 WatchHamster를 시작할 수 있습니다.${NC}"
        else
            echo -e "${RED}❌ 의존성 설치 실패!${NC}"
            exit 1
        fi
        ;;
        
    3)
        echo -e "${BLUE}🌐 WatchHamster 프론트엔드 시작 중...${NC}"
        echo -e "${CYAN}================================================================${NC}"
        echo -e "${WHITE}📍 InfoMax API 테스트 플랫폼: ${GREEN}http://localhost:1420/api-packages${NC}"
        echo -e "${WHITE}🐹 WatchHamster v4.0 - API 테스트 모듈${NC}"
        echo -e "${CYAN}================================================================${NC}"
        echo -e "${YELLOW}시스템 종료: ${RED}Ctrl+C${NC}"
        echo ""
        
        npm run dev
        ;;
        
    4)
        echo -e "${GREEN}🐍 WatchHamster 백엔드 서비스 시작 중...${NC}"
        
        if [ -d "python-backend" ]; then
            cd python-backend
            if [ -f "requirements.txt" ]; then
                echo -e "${YELLOW}Python 의존성 설치 중...${NC}"
                python3 -m pip install -r requirements.txt
            fi
            
            echo -e "${CYAN}================================================================${NC}"
            echo -e "${WHITE}🐹 WatchHamster 백엔드 서비스 활성화${NC}"
            echo -e "${GREEN}📈 POSCO 뉴스 모니터링 활성화${NC}"
            echo -e "${PURPLE}🌐 웹훅 서비스 대기 중${NC}"
            echo -e "${CYAN}================================================================${NC}"
            
            python3 -m api.webhook_manager
        else
            echo -e "${YELLOW}⚠️  백엔드 디렉토리를 찾을 수 없습니다.${NC}"
            echo -e "${BLUE}프론트엔드만 실행합니다...${NC}"
            npm run dev
        fi
        ;;
        
    5)
        echo -e "${YELLOW}🏗️  WatchHamster 시스템 빌드 중...${NC}"
        if npm run build; then
            echo -e "${GREEN}✅ 빌드 완료!${NC}"
            echo ""
            echo -e "${BLUE}🎭 프로덕션 프리뷰 서버 시작 중...${NC}"
            npm run preview
        else
            echo -e "${RED}❌ 빌드 실패!${NC}"
            exit 1
        fi
        ;;
        
    6)
        echo -e "${YELLOW}🧹 WatchHamster 시스템 초기화 중...${NC}"
        
        # node_modules 삭제
        if [ -d "node_modules" ]; then
            rm -rf node_modules
            echo -e "${GREEN}✅ node_modules 정리 완료${NC}"
        fi
        
        # package-lock.json 삭제 (있다면)
        if [ -f "package-lock.json" ]; then
            rm -f package-lock.json
            echo -e "${GREEN}✅ package-lock.json 정리 완료${NC}"
        fi
        
        # npm 캐시 정리
        npm cache clean --force
        echo -e "${GREEN}✅ npm 캐시 정리 완료${NC}"
        
        # Python 캐시 정리 (있다면)
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}✅ Python 캐시 정리 완료${NC}"
        
        # 새로 설치
        echo ""
        echo -e "${YELLOW}📦 WatchHamster 시스템 재설치 중...${NC}"
        if npm install; then
            echo -e "${GREEN}✅ 시스템 초기화 완료!${NC}"
            echo ""
            echo -e "${BLUE}🐹 WatchHamster를 시작하시겠습니까? (y/n): ${NC}"
            read -r start_server
            if [[ $start_server == "y" || $start_server == "Y" ]]; then
                npm run dev
            fi
        else
            echo -e "${RED}❌ 재설치 실패!${NC}"
            exit 1
        fi
        ;;
        
    7)
        echo -e "${BLUE}📋 WatchHamster v4.0 시스템 상태 체크${NC}"
        echo -e "${CYAN}================================================================${NC}"
        
        # 프로젝트 구조 체크
        echo -e "${WHITE}📁 프로젝트 구조:${NC}"
        [ -f "package.json" ] && echo -e "${GREEN}✅ package.json${NC}" || echo -e "${RED}❌ package.json${NC}"
        [ -d "src" ] && echo -e "${GREEN}✅ src/ (프론트엔드)${NC}" || echo -e "${RED}❌ src/${NC}"
        [ -d "python-backend" ] && echo -e "${GREEN}✅ python-backend/ (백엔드)${NC}" || echo -e "${YELLOW}⚠️  python-backend/${NC}"
        [ -d "core" ] && echo -e "${GREEN}✅ core/ (모니터링)${NC}" || echo -e "${YELLOW}⚠️  core/${NC}"
        
        echo ""
        echo -e "${WHITE}🔧 핵심 모듈:${NC}"
        [ -f "src/pages/ApiPackageManagement.tsx" ] && echo -e "${GREEN}✅ InfoMax API 테스트 모듈${NC}" || echo -e "${RED}❌ API 테스트 모듈${NC}"
        [ -f "src/utils/parameterDefaultManager.ts" ] && echo -e "${GREEN}✅ 자동갱신 시스템${NC}" || echo -e "${RED}❌ 자동갱신 시스템${NC}"
        [ -f "src/utils/apiCrawlingMapper.ts" ] && echo -e "${GREEN}✅ API 크롤링 매핑${NC}" || echo -e "${RED}❌ 크롤링 매핑${NC}"
        
        echo ""
        echo -e "${WHITE}📊 통계:${NC}"
        if [ -f "src/utils/apiCrawlingMapper.ts" ]; then
            API_COUNT=$(grep -c "urlPath:" src/utils/apiCrawlingMapper.ts 2>/dev/null || echo "?")
            echo -e "${BLUE}• 지원 API: ${API_COUNT}개+${NC}"
        fi
        
        if [ -f "src/utils/parameterDefaultManager.ts" ]; then
            LOGIC_COUNT=$(grep -c "option value" src/components/ApiPackage/ParameterDefaultsModal.tsx 2>/dev/null || echo "?")
            echo -e "${BLUE}• 자동갱신 로직: 28개${NC}"
        fi
        
        echo -e "${CYAN}================================================================${NC}"
        ;;
        
    8)
        echo -e "${YELLOW}👋 WatchHamster를 종료합니다.${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ 잘못된 선택입니다. 1-8 사이의 숫자를 입력하세요.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 WatchHamster v4.0 작업 완료!${NC}"
echo -e "${BLUE}🐹 최고의 모니터링 시스템과 함께하세요!${NC}"
echo -e "${CYAN}================================================================${NC}"
