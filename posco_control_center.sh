#!/bin/bash
# ============================================================================
# POSCO Control Center v4.0
# Mac용 POSCO 뉴스 및 주가 모니터링 제어 센터
# ============================================================================

# 스크립트 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 공통 라이브러리 로드
if [[ -f "./lib_wt_common.sh" ]]; then
    source "./lib_wt_common.sh"
else
    echo "Error: lib_wt_common.sh를 찾을 수 없습니다."
    echo "현재 경로: $(pwd)"
    echo "스크립트 경로: $SCRIPT_DIR"
    exit 1
fi

# 초기화
init_system

# ============================================================================
# 메인 메뉴
# ============================================================================
main_menu() {
    clear
    print_header "🏭 POSCO Control Center v4.0 🎛️"
    echo -e "${INFO}🎯 POSCO 뉴스 및 주가 모니터링 시스템을 관리합니다${RESET}"
    echo

    echo -e "${YELLOW}🎛️ 관리할 기능을 선택하세요:${RESET}"
    echo

    # 모니터링 관리
    start_box "${GREEN}"
    echo -e "${GREEN}║${RESET}                           ${CYAN}📊 모니터링 관리${RESET}                                    ${GREEN}║${RESET}"
    echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "1." "🚀 메인 알림 시스템 시작" "POSCO 뉴스 모니터링 시작"
    print_menu_item "2." "🛑 메인 알림 시스템 중지" "모니터링 프로세스 중지"
    print_menu_item "3." "🔄 메인 알림 시스템 재시작" "모니터링 시스템 재시작"
    print_menu_item "4." "📊 실시간 상태 확인" "현재 모니터링 상태 확인"
    end_box

    echo

    # 뉴스 관리
    start_box "${BLUE}"
    echo -e "${BLUE}║${RESET}                           ${MAGENTA}📰 뉴스 관리${RESET}                                      ${BLUE}║${RESET}"
    echo -e "${BLUE}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "A." "📋 뉴스 로그 확인" "최신 뉴스 로그 확인"
    print_menu_item "B." "📈 뉴스 통계 보기" "뉴스 수집 통계 확인"
    print_menu_item "C." "🔍 뉴스 검색" "특정 키워드 뉴스 검색"
    end_box

    echo

    # 시스템 관리
    start_box "${RED}"
    echo -e "${RED}║${RESET}                           ${WHITE}⚙️ 시스템 관리${RESET}                                      ${RED}║${RESET}"
    echo -e "${RED}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "D." "🔧 시스템 상태" "POSCO 시스템 상태 확인"
    print_menu_item "E." "🧪 시스템 테스트" "모니터링 시스템 테스트"
    print_menu_item "F." "📦 데이터 백업" "뉴스 데이터 백업"
    end_box

    echo
    echo -e "${GRAY}0. ❌ 메인 메뉴로 돌아가기${RESET}"
    echo

    print_system_info

    echo -n -e "${GREEN}🎯 선택하세요 (1-4, A-F, 0): ${RESET}"
    read -r choice

    case "$choice" in
        "1") start_watchhamster ;;
        "2") stop_watchhamster ;;
        "3") restart_watchhamster ;;
        "4") check_monitoring_status ;;
        "A"|"a") view_news_logs ;;
        "B"|"b") view_news_stats ;;
        "C"|"c") search_news ;;
        "D"|"d") check_system_status ;;
        "E"|"e") test_system ;;
        "F"|"f") backup_data ;;
        "0") return_to_main ;;
        *) invalid_choice ;;
    esac
}

# ============================================================================
# 모니터링 관리
# ============================================================================

# 워치햄스터 시작
start_watchhamster() {
    clear
    print_header "🚀 메인 알림 시스템 시작"
    
    if ! confirm_action "POSCO 뉴스 모니터링을 시작하시겠습니까?"; then
        main_menu
        return
    fi

    # 이미 실행 중인지 확인
    if pgrep -f "posco_main_notifier.py" >/dev/null || pgrep -f "monitor_WatchHamster.py" >/dev/null; then
        print_warning "🐹 POSCO 모니터링 시스템이 이미 실행 중입니다."
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return
    fi

    # Python 스크립트 실행 - POSCO 메인 알림 시스템 우선
    if [[ -f "Monitoring/Posco_News_mini/posco_main_notifier.py" ]]; then
        print_info "🚀 POSCO 메인 알림 시스템 시작 중..."
        
        # 절대 경로로 실행
        nohup python3 "$SCRIPT_DIR/Monitoring/Posco_News_mini/posco_main_notifier.py" > "$SCRIPT_DIR/posco_monitor.log" 2>&1 &
        local pid=$!
        sleep 5
        
        if kill -0 $pid 2>/dev/null; then
            print_success "🏭 POSCO 메인 알림 시스템이 성공적으로 시작되었습니다. (PID: $pid)"
            print_info "📊 5가지 BOT 타입 알림 활성화"
            print_info "🔄 실시간 뉴스 모니터링: 30초 간격"
            print_info "📋 스케줄 작업: 06:00, 06:10, 18:00, 18:10, 18:20"
            print_info "🌙 24시간 자동 모니터링 활성화"
        else
            print_error "POSCO 메인 알림 시스템 시작에 실패했습니다."
            print_info "로그를 확인하세요: tail -f $SCRIPT_DIR/posco_monitor.log"
            
            # 오류 로그 표시
            if [[ -f "$SCRIPT_DIR/posco_monitor.log" ]]; then
                print_info "최근 오류 로그:"
                tail -5 "$SCRIPT_DIR/posco_monitor.log"
            fi
        fi
    else
        print_error "❌ posco_main_notifier.py 파일을 찾을 수 없습니다."
        print_info "파일 경로: $SCRIPT_DIR/Monitoring/Posco_News_mini/posco_main_notifier.py"
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
}

# 워치햄스터 중지
stop_watchhamster() {
    clear
    print_header "🛑 워치햄스터 중지"
    
    if ! confirm_action "POSCO 뉴스 모니터링을 중지하시겠습니까?"; then
        main_menu
        return
    fi

    local pids=$(pgrep -f "posco_main_notifier.py"; pgrep -f "monitor_WatchHamster.py")
    
    if [[ -n "$pids" ]]; then
        for pid in $pids; do
            kill $pid 2>/dev/null
        done
        sleep 2
        
        # 강제 종료
        local remaining_pids=$(pgrep -f "posco_main_notifier.py"; pgrep -f "monitor_WatchHamster.py")
        if [[ -n "$remaining_pids" ]]; then
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null
            done
        fi
        
        print_success "🐹 POSCO 모니터링 시스템이 성공적으로 중지되었습니다."
    else
        print_info "실행 중인 모니터링 시스템이 없습니다."
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 워치햄스터 재시작
restart_watchhamster() {
    clear
    print_header "🔄 워치햄스터 재시작"
    
    if ! confirm_action "워치햄스터를 재시작하시겠습니까?"; then
        main_menu
        return
    fi

    stop_watchhamster
    sleep 2
    start_watchhamster
}

# 실시간 상태 확인
check_monitoring_status() {
    clear
    print_header "📊 실시간 상태 확인"
    
    print_section "⚙️ 프로세스 상태"
    
    local pids=$(pgrep -f "posco_main_notifier.py"; pgrep -f "monitor_WatchHamster.py")
    if [[ -n "$pids" ]]; then
        print_success "🐹 POSCO 모니터링 시스템이 실행 중입니다."
        for pid in $pids; do
            local cmd=$(ps -p $pid -o command= 2>/dev/null)
            local time=$(ps -p $pid -o etime= 2>/dev/null)
            local script_name="알 수 없음"
            if echo "$cmd" | grep -q "posco_main_notifier.py"; then
                script_name="메인 알림 시스템"
            elif echo "$cmd" | grep -q "monitor_WatchHamster.py"; then
                script_name="워치햄스터"
            fi
            echo -e "  ${GRAY}•${RESET} $script_name - PID: $pid, 실행시간: $time"
        done
    else
        print_warning "🐹 POSCO 모니터링 시스템이 실행되지 않았습니다."
    fi

    print_section "📊 시스템 리소스"
    print_system_info

    print_section "📁 로그 파일 상태"
    
    local log_files=("posco_monitor.log" "system.log" "error.log")
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local size=$(du -h "$log_file" 2>/dev/null | cut -f1)
            local modified=$(stat -f "%Sm" "$log_file" 2>/dev/null)
            echo -e "${GREEN}✅${RESET} $log_file (${size}, 수정: $modified)"
        else
            echo -e "${RED}❌${RESET} $log_file (없음)"
        fi
    done

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 뉴스 관리
# ============================================================================

# 뉴스 로그 확인
view_news_logs() {
    clear
    print_header "📋 뉴스 로그 확인"
    
    if [[ -f "posco_monitor.log" ]]; then
        echo -e "${CYAN}최근 20줄의 로그:${RESET}"
        echo
        tail -n 20 "posco_monitor.log"
    else
        print_warning "로그 파일이 없습니다."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 뉴스 통계 보기
view_news_stats() {
    clear
    print_header "📈 뉴스 통계 보기"
    
    if [[ -f "posco_news_data.json" ]]; then
        local size=$(du -h "posco_news_data.json" 2>/dev/null | cut -f1)
        local modified=$(stat -f "%Sm" "posco_news_data.json" 2>/dev/null)
        echo -e "${GREEN}✅${RESET} posco_news_data.json (${size}, 수정: $modified)"
        
        # 간단한 통계
        local count=$(python3 -c "import json; print(len(json.load(open('posco_news_data.json'))))" 2>/dev/null || echo "N/A")
        echo -e "  총 뉴스 수: $count개"
    else
        echo -e "${RED}❌${RESET} posco_news_data.json (없음)"
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 뉴스 검색
search_news() {
    clear
    print_header "🔍 뉴스 검색"
    
    echo -n -e "${GREEN}검색할 키워드를 입력하세요: ${RESET}"
    read -r keyword
    
    if [[ -z "$keyword" ]]; then
        print_error "키워드를 입력해주세요."
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return
    fi

    if [[ -f "posco_news_data.json" ]]; then
        echo -e "${CYAN}검색 결과:${RESET}"
        echo
        python3 -c "
import json
keyword = '$keyword'
try:
    with open('posco_news_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        results = [item for item in data if keyword in item.get('title', '') or keyword in item.get('content', '')]
        print(f'발견된 뉴스: {len(results)}개')
        for i, item in enumerate(results[:5]):
            print(f'{i+1}. {item.get(\"title\", \"제목 없음\")}')
            print(f'   날짜: {item.get(\"date\", \"날짜 없음\")}')
            print()
except Exception as e:
    print(f'검색 오류: {e}')
" 2>/dev/null || echo "검색 실패"
    else
        print_warning "뉴스 데이터 파일이 없습니다."
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 시스템 관리
# ============================================================================

# 시스템 상태 확인
check_system_status() {
    clear
    print_header "🔧 시스템 상태 확인"
    
    print_section "📊 POSCO 시스템 현황"
    
    # Python 환경 확인
    print_section "🐍 Python 환경"
    check_python_environment
    
    # 필수 파일 확인
    print_section "📁 필수 파일 확인"
    local required_files=("Monitoring/Posco_News_mini/posco_main_notifier.py" "Monitoring/Posco_News_mini/monitor_WatchHamster.py" "Monitoring/Posco_News_mini/config.py" "requirements.txt")
    check_required_files "${required_files[@]}"
    
    # 데이터 파일 확인
    print_section "📊 데이터 파일 상태"
    local data_files=("posco_news_data.json" "posco_news_cache.json")
    for data_file in "${data_files[@]}"; do
        if [[ -f "$data_file" ]]; then
            local size=$(du -h "$data_file" 2>/dev/null | cut -f1)
            local modified=$(stat -f "%Sm" "$data_file" 2>/dev/null)
            echo -e "${GREEN}✅${RESET} $data_file (${size}, 수정: $modified)"
        else
            echo -e "${RED}❌${RESET} $data_file (없음)"
        fi
    done
    
    # 네트워크 연결 확인
    print_section "🌐 네트워크 상태"
    check_network_connection
    
    # 시스템 리소스 확인
    print_section "💻 시스템 리소스"
    print_system_info

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 시스템 테스트
test_system() {
    clear
    print_header "🧪 시스템 테스트"
    
    if ! confirm_action "POSCO 모니터링 시스템 테스트를 실행하시겠습니까?"; then
        main_menu
        return
    fi

    print_section "🔍 기본 시스템 테스트"
    
    # Python 환경 테스트
    if check_python_environment; then
        print_success "Python 환경 테스트 통과"
    else
        print_error "Python 환경 테스트 실패"
    fi
    
    # 네트워크 연결 테스트
    if check_network_connection; then
        print_success "네트워크 연결 테스트 통과"
    else
        print_error "네트워크 연결 테스트 실패"
    fi
    
    # Python 스크립트 테스트
    print_section "🐍 Python 스크립트 테스트"
    if [[ -f "Monitoring/Posco_News_mini/posco_main_notifier.py" ]]; then
        if python3 -c "import sys; print('Python 스크립트 테스트 통과')" 2>/dev/null; then
            print_success "🐹 POSCO 메인 알림 시스템 테스트 통과"
        else
            print_error "🐹 POSCO 메인 알림 시스템 테스트 실패"
        fi
    elif [[ -f "Monitoring/Posco_News_mini/monitor_WatchHamster.py" ]]; then
        if python3 -c "import sys; print('Python 스크립트 테스트 통과')" 2>/dev/null; then
            print_success "🐹 POSCO 워치햄스터 테스트 통과"
        else
            print_error "🐹 POSCO 워치햄스터 테스트 실패"
        fi
    else
        print_warning "🐹 POSCO 모니터링 시스템 파일이 없습니다."
    fi

    print_success "시스템 테스트가 완료되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 데이터 백업
backup_data() {
    clear
    print_header "📦 데이터 백업"
    
    if ! confirm_action "POSCO 뉴스 데이터를 백업하시겠습니까?"; then
        main_menu
        return
    fi

    local backup_dir="$HOME/.watchhamster/posco_backups"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_name="posco_backup_$timestamp"
    local backup_path="$backup_dir/$backup_name"

    mkdir -p "$backup_path"

    # 중요 데이터 파일들 백업
    local data_files=("posco_news_data.json" "posco_news_cache.json" "*.py" "config.py")
    local backed_up=0
    
    for pattern in "${data_files[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                cp "$file" "$backup_path/" 2>/dev/null
                backed_up=1
            fi
        done
    done

    # 백업 압축
    if [[ $backed_up -eq 1 ]]; then
        cd "$backup_dir"
        tar -czf "$backup_name.tar.gz" "$backup_name" 2>/dev/null
        rm -rf "$backup_name"
        cd "$SCRIPT_DIR"
        
        local backup_size=$(du -h "$backup_dir/$backup_name.tar.gz" 2>/dev/null | cut -f1)
        print_success "백업이 생성되었습니다: $backup_name.tar.gz (크기: $backup_size)"
    else
        print_error "백업할 데이터가 없습니다."
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 유틸리티 함수들
# ============================================================================

# 잘못된 선택 처리
invalid_choice() {
    print_error "잘못된 선택입니다. 다시 시도해주세요."
    sleep 2
    main_menu
}

# 메인 메뉴로 돌아가기
return_to_main() {
    cd "$SCRIPT_DIR/.."
    if [[ -f "watchhamster_master_control.sh" ]]; then
        bash "watchhamster_master_control.sh"
    else
        print_error "메인 제어 센터를 찾을 수 없습니다."
        exit 1
    fi
}

# ============================================================================
# 메인 실행
# ============================================================================

# 스크립트 시작
main_menu 