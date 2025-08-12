#!/bin/bash
# ============================================================================
# Posco WatchHamster v3.0 제어센터
# POSCO 시스템 제어센터
# 
# WatchHamster v3.0 및 POSCO News 250808 호환
# Created: 2025-08-08
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
RESET='\033[0m'

# 터미널 설정
clear
echo -e "${CYAN}🐹 POSCO 워치햄스터 v3.0 macOS 제어센터 🎛️${RESET}"

main_menu() {
    clear
    echo -e "${CYAN}================================================================================${RESET}"
    echo -e "${CYAN}                   🐹 POSCO 워치햄스터 v3.0 통합 제어센터 🎛️${RESET}"
    echo -e "${CYAN}================================================================================${RESET}"
    echo -e "${BLUE}🎯 워치햄스터 v3.0이 모든 POSCO 모니터링 시스템을 통합 관리합니다${RESET}"
    echo

    echo -e "${YELLOW}🐹 워치햄스터 제어 메뉴를 선택하세요:${RESET}"
    echo

    # 워치햄스터 관리 (최상위)
    echo -e "${GREEN}┌─────────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${GREEN}│${RESET}                           ${CYAN}🐹 워치햄스터 v3.0 통합 관리${RESET}                        ${GREEN}│${RESET}"
    echo -e "${GREEN}├─────────────────────────────────────────────────────────────────────────────┤${RESET}"
    echo -e "${GREEN}│${RESET}  1. 🚀 워치햄스터 시작        - 전체 모니터링 시스템 시작                    ${GREEN}│${RESET}"
    echo -e "${GREEN}│${RESET}  2. 🛑 워치햄스터 중지        - 전체 모니터링 시스템 중지                    ${GREEN}│${RESET}"
    echo -e "${GREEN}│${RESET}  3. 🔄 워치햄스터 재시작      - 전체 모니터링 시스템 재시작                  ${GREEN}│${RESET}"
    echo -e "${GREEN}│${RESET}  4. 📊 워치햄스터 상태        - 전체 시스템 상태 확인                        ${GREEN}│${RESET}"
    echo -e "${GREEN}│${RESET}  5. 🔧 모듈 관리             - 개별 모듈 상태 및 제어                        ${GREEN}│${RESET}"
    echo -e "${GREEN}└─────────────────────────────────────────────────────────────────────────────┘${RESET}"
    echo

    # v3.0 혁신 기능
    echo -e "${MAGENTA}┌─────────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${MAGENTA}│${RESET}                           ${WHITE}🚀 v3.0 혁신 기능${RESET}                                ${MAGENTA}│${RESET}"
    echo -e "${MAGENTA}├─────────────────────────────────────────────────────────────────────────────┤${RESET}"
    echo -e "${MAGENTA}│${RESET}  G. 🚀 성능 모니터링         - 실시간 성능 분석 및 최적화                   ${MAGENTA}│${RESET}"
    echo -e "${MAGENTA}│${RESET}  H. 📊 최적화 보고서         - AI 기반 시스템 최적화 권장사항               ${MAGENTA}│${RESET}"
    echo -e "${MAGENTA}│${RESET}  I. 🧪 종합 테스트          - v3.0 전체 시스템 검증                       ${MAGENTA}│${RESET}"
    echo -e "${MAGENTA}│${RESET}  J. 🔍 통합 검증            - 최종 시스템 통합 검증                        ${MAGENTA}│${RESET}"
    echo -e "${MAGENTA}└─────────────────────────────────────────────────────────────────────────────┘${RESET}"
    echo

    # 뉴스 관리
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${BLUE}│${RESET}                              ${MAGENTA}📰 뉴스 관리${RESET}                                   ${BLUE}│${RESET}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────────────────────┤${RESET}"
    echo -e "${BLUE}│${RESET}  A. 📋 뉴스 로그 확인         - 최신 뉴스 로그 확인                          ${BLUE}│${RESET}"
    echo -e "${BLUE}│${RESET}  B. 📈 뉴스 통계 보기         - 뉴스 수집 통계 확인                          ${BLUE}│${RESET}"
    echo -e "${BLUE}│${RESET}  C. 🔍 뉴스 검색             - 특정 키워드 뉴스 검색                         ${BLUE}│${RESET}"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────────────────┘${RESET}"
    echo

    echo -e "${GRAY}0. ❌ 종료${RESET}"
    echo

    # 시스템 정보
    echo -e "${GRAY}┌─────────────────────────────────────────────────────────────────────────────┐${RESET}"
    echo -e "${GRAY}│${RESET} 💻 시스템: macOS | 시간: $(date '+%Y-%m-%d %H:%M:%S')                        ${GRAY}│${RESET}"
    echo -e "${GRAY}│${RESET} 📁 작업 디렉토리: $PWD                                                      ${GRAY}│${RESET}"
    echo -e "${GRAY}└─────────────────────────────────────────────────────────────────────────────┘${RESET}"
    echo

    echo -n -e "${GREEN}🎯 선택하세요 (1-5, A-C, G-J, 0): ${RESET}"
    read -r choice

    case "$choice" in
        "1") start_watchhamster ;;
        "2") stop_watchhamster ;;
        "3") restart_watchhamster ;;
        "4") check_status ;;
        "5") manage_modules ;;
        "A"|"a") view_news_logs ;;
        "B"|"b") view_news_stats ;;
        "C"|"c") search_news ;;
        "G"|"g") performance_monitor ;;
        "H"|"h") optimization_report ;;
        "I"|"i") comprehensive_test ;;
        "J"|"j") integration_verification ;;
        "0") exit_program ;;
        *) invalid_choice ;;
    esac
}

start_watchhamster() {
    clear
    echo -e "${GREEN}🚀 워치햄스터 v3.0 시작${RESET}"
    echo -e "${CYAN}================================================================================${RESET}"
    echo

    echo -e "${BLUE}🔍 시스템 환경 체크 중...${RESET}"
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3가 설치되지 않았습니다${RESET}"
        echo -e "${YELLOW}💡 Python 3.7 이상을 설치해주세요${RESET}"
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return 1
    fi
    echo -e "${GREEN}✅ Python 환경 확인 완료${RESET}"
    
    # 워치햄스터 스크립트 확인
    if [[ ! -f "Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py" ]]; then
        echo -e "${RED}❌ 워치햄스터 스크립트를 찾을 수 없습니다${RESET}"
        echo -e "${YELLOW}📁 경로: $SCRIPT_DIR/Monitoring/Posco_News_mini/monitor_WatchHamster_v3.0.py${RESET}"
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return 1
    fi
    echo -e "${GREEN}✅ 워치햄스터 스크립트 확인 완료${RESET}"
    
    echo
    echo -e "${BLUE}🧹 기존 프로세스 정리 중...${RESET}"
    pkill -f "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py" 2>/dev/null || true
    sleep 2
    
    echo
    echo -e "${GREEN}🐹 워치햄스터 v3.0 시작 중...${RESET}"
    cd "Monitoring/Posco_News_mini"
    
    nohup python3 Monitoring/POSCO_News_250808/monitor_WatchHamster_v3.0.py > ../../watchhamster.log 2>&1 &
    WATCHHAMSTER_PID=$!
    cd "$SCRIPT_DIR"
    
    echo -e "${BLUE}⏳ 시스템 초기화 대기 중 (10초)...${RESET}"
    sleep 10
    
    if kill -0 $WATCHHAMSTER_PID 2>/dev/null; then
        echo -e "${GREEN}✅ 워치햄스터 v3.0이 성공적으로 시작되었습니다! (PID: $WATCHHAMSTER_PID)${RESET}"
        echo
        echo -e "${CYAN}🎉 v3.0 혁신 기능들이 활성화되었습니다:${RESET}"
        echo -e "${WHITE}  • 3단계 지능적 복구 시스템${RESET}"
        echo -e "${WHITE}  • 실시간 성능 모니터링${RESET}"
        echo -e "${WHITE}  • 향상된 알림 시스템${RESET}"
        echo -e "${WHITE}  • 자동 최적화 기능${RESET}"
        echo -e "${WHITE}  • 하이브리드 아키텍처${RESET}"
    else
        echo -e "${RED}❌ 워치햄스터 시작 실패${RESET}"
        if [[ -f ".naming_backup/config_data_backup/watchhamster.log" ]]; then
            echo -e "${YELLOW}최근 오류 로그:${RESET}"
            tail -10 ".naming_backup/config_data_backup/watchhamster.log"
        fi
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

performance_monitor() {
    clear
    echo -e "${MAGENTA}🚀 POSCO 워치햄스터 v3.0 성능 모니터링${RESET}"
    echo -e "${CYAN}================================================================================${RESET}"
    echo
    echo -e "${BLUE}📊 실시간 성능 분석을 시작합니다...${RESET}"
    echo

    if [[ -f "demo_performance_monitoring.py" ]]; then
        echo -e "${GREEN}🎯 v3.0 성능 모니터링 데모 실행 중...${RESET}"
        python3 demo_performance_monitoring.py
        echo
        echo -e "${GREEN}✅ 성능 모니터링 완료!${RESET}"
    else
        echo -e "${RED}❌ 성능 모니터링 스크립트를 찾을 수 없습니다.${RESET}"
        echo -e "${YELLOW}📁 파일: demo_performance_monitoring.py${RESET}"
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

optimization_report() {
    clear
    echo -e "${MAGENTA}📊 시스템 최적화 보고서 생성${RESET}"
    echo -e "${CYAN}================================================================================${RESET}"
    echo
    echo -e "${BLUE}🔍 시스템 분석 및 최적화 권장사항 생성 중...${RESET}"
    echo

    if [[ -f "system_optimization_report_generator.py" ]]; then
        echo -e "${GREEN}🎯 v3.0 최적화 분석 실행 중...${RESET}"
        python3 system_optimization_report_generator.py
        echo
        echo -e "${GREEN}✅ 최적화 보고서 생성 완료!${RESET}"
        echo -e "${CYAN}📄 보고서 파일: system_optimization_report.md${RESET}"
    else
        echo -e "${RED}❌ 최적화 보고서 생성기를 찾을 수 없습니다.${RESET}"
        echo -e "${YELLOW}📁 파일: system_optimization_report_generator.py${RESET}"
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

integration_verification() {
    clear
    echo -e "${MAGENTA}🔍 최종 시스템 통합 검증${RESET}"
    echo -e "${CYAN}================================================================================${RESET}"
    echo
    echo -e "${BLUE}🎯 v3.0 시스템 통합 및 검증을 실행합니다...${RESET}"
    echo

    if [[ -f "final_system_integration_verification.py" ]]; then
        echo -e "${GREEN}🎯 v3.0 최종 통합 검증 실행 중...${RESET}"
        python3 final_system_integration_verification.py
        echo
        echo -e "${GREEN}✅ 통합 검증 완료!${RESET}"
    else
        echo -e "${RED}❌ 통합 검증 스크립트를 찾을 수 없습니다.${RESET}"
        echo -e "${YELLOW}📁 파일: final_system_integration_verification.py${RESET}"
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

exit_program() {
    clear
    echo
    echo -e "${CYAN}👋 POSCO 워치햄스터 v3.0 제어센터를 종료합니다.${RESET}"
    echo
    echo -e "${GREEN}🎉 v3.0 혁신적 모니터링 시스템을 이용해주셔서 감사합니다!${RESET}"
    echo
    exit 0
}

invalid_choice() {
    echo -e "${RED}❌ 잘못된 선택입니다. 다시 시도해주세요.${RESET}"
    sleep 2
    main_menu
}

# 메인 실행
main_menu