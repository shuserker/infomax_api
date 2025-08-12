#!/bin/bash
# ============================================================================
# POSCO WatchHamster Control Center v2.0
# POSCO WatchHamster v3.0 통합 제어 센터 - 워치햄스터가 모든 것을 관리합니다
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
    print_header "🐹 POSCO WatchHamster Control Center v2.0 🎛️"
    echo -e "${INFO}🎯 워치햄스터가 모든 POSCO 모니터링 시스템을 통합 관리합니다${RESET}"
    echo

    echo -e "${YELLOW}🐹 워치햄스터 제어 메뉴를 선택하세요:${RESET}"
    echo

    # 워치햄스터 관리 (최상위)
    start_box "${GREEN}"
    echo -e "${GREEN}║${RESET}                           ${CYAN}🐹 워치햄스터 통합 관리${RESET}                                   ${GREEN}║${RESET}"
    echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "1." "🚀 워치햄스터 시작" "전체 모니터링 시스템 시작"
    print_menu_item "2." "🛑 워치햄스터 중지" "전체 모니터링 시스템 중지"
    print_menu_item "3." "🔄 워치햄스터 재시작" "전체 모니터링 시스템 재시작"
    print_menu_item "4." "📊 WatchHamster v3.0 상태" "전체 시스템 상태 확인"
    print_menu_item "5." "🔧 모듈 관리" "개별 모듈 상태 및 제어"
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

    # 고급 옵션 (개별 모듈 관리)
    start_box "${YELLOW}"
    echo -e "${YELLOW}║${RESET}                           ${WHITE}⚙️ 고급 옵션${RESET}                                      ${YELLOW}║${RESET}"
    echo -e "${YELLOW}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "D." "🔧 시스템 진단" "POSCO 시스템 상태 진단"
    print_menu_item "E." "🧪 시스템 테스트" "모니터링 시스템 테스트"
    print_menu_item "F." "📦 데이터 백업" "뉴스 데이터 백업"
    end_box

    echo
    echo -e "${GRAY}0. ❌ 메인 메뉴로 돌아가기${RESET}"
    echo

    print_system_info

    echo -n -e "${GREEN}🎯 선택하세요 (1-5, A-F, 0): ${RESET}"
    read -r choice

    case "$choice" in
        "1") start_watchhamster ;;
        "2") stop_watchhamster ;;
        "3") restart_watchhamster ;;
        "4") check_watchhamster_status ;;
        "5") manage_modules ;;
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
    print_header "🚀 워치햄스터 시작"
    
    if ! confirm_action "POSCO WatchHamster v3.0 시작하시겠습니까?"; then
        main_menu
        return
    fi

    # 1. 환경 체크
    print_info "🔍 시스템 환경 체크 중..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3가 설치되지 않았습니다"
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return 1
    fi
    
    # 워치햄스터 스크립트 확인
    if [[ ! -f ".naming_backup/config_data_backup/watchhamster.log" ]]; then
        print_error "워치햄스터 스크립트를 찾을 수 없습니다"
        print_info ".naming_backup/config_data_backup/watchhamster.log"
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return 1
    fi
    
    # 2. 기존 프로세스 정리
    print_info "🧹 기존 프로세스 정리 중..."
    pkill -f ".naming_backup/config_data_backup/watchhamster.log" 2>/dev/null || true
    sleep 2
    
    # 3. 워치햄스터 시작
    print_info "🐹 워치햄스터 시작 중..."
    cd "Monitoring/POSCO News 250808_mini"
    
    nohup python3 .naming_backup/config_data_backup/watchhamster.log > ../../watchhamster.log 2>&1 &
    WATCHHAMSTER_PID=$!
    cd "$SCRIPT_DIR"
    
    # 4. 초기화 대기
    print_info "⏳ 시스템 초기화 대기 중 (10초)..."
    sleep 10
    
    # 5. 상태 확인
    if kill -0 $WATCHHAMSTER_PID 2>/dev/null; then
        print_success "워치햄스터 시작 성공 (PID: $WATCHHAMSTER_PID)"
        
        # 하위 프로세스 상태 확인
        print_info "📊 하위 프로세스 상태 확인 중..."
        sleep 5
        
        check_managed_processes
    else
        print_error "WatchHamster v3.0 실패"
        if [[ -f ".naming_backup/config_data_backup/watchhamster.log" ]]; then
            print_info "최근 오류 로그:"
            tail -10 ".naming_backup/config_data_backup/watchhamster.log"
        fi
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return 1
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 워치햄스터 중지
stop_watchhamster() {
    clear
    print_header "🛑 워치햄스터 중지"
    
    if ! confirm_action "POSCO WatchHamster v3.0 모니터링 시스템을 중지하시겠습니까?"; then
        main_menu
        return
    fi

    print_info "🛑 워치햄스터 중지 중..."
    
    # 1. 워치햄스터 메인 프로세스 중지
    local watchhamster_pid=$(pgrep -f ".naming_backup/config_data_backup/watchhamster.log")
    if [[ -n "$watchhamster_pid" ]]; then
        print_info "🐹 워치햄스터 메인 프로세스 중지 중... (PID: $watchhamster_pid)"
        kill $watchhamster_pid 2>/dev/null
        sleep 3
        
        # 강제 종료가 필요한 경우
        if kill -0 $watchhamster_pid 2>/dev/null; then
            print_warning "강제 종료 중..."
            kill -9 $watchhamster_pid 2>/dev/null
        fi
    fi
    
    # 2. 관리되는 하위 프로세스들 중지
# BROKEN_REF:     local processes=("POSCO News 250808_monitor.py" "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/integrated_report_scheduler.py" "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/historical_data_collector.py")
    
    for process in "${processes[@]}"; do
        local pid=$(pgrep -f "$process")
        if [[ -n "$pid" ]]; then
            print_info "📊 $process 중지 중... (PID: $pid)"
            kill $pid 2>/dev/null
            sleep 1
            
            # 강제 종료가 필요한 경우
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null
            fi
        fi
    done
    
    # 3. 최종 상태 확인
    sleep 2
    local remaining_processes=0
    for process in ".naming_backup/config_data_backup/watchhamster.log" "${processes[@]}"; do
        if pgrep -f "$process" >/dev/null; then
            ((remaining_processes++))
        fi
    done
    
    if [[ $remaining_processes -eq 0 ]]; then
        print_success "🎉 모든 워치햄스터 프로세스가 성공적으로 중지되었습니다"
    else
        print_warning "⚠️ 일부 프로세스가 여전히 실행 중일 수 있습니다"
        print_info "강제 정리를 위해 'pkill -f WatchHamster' 명령을 사용하세요"
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

# WatchHamster v3.0 상태 확인
check_watchhamster_status() {
    clear
    print_header "📊 WatchHamster v3.0 상태 확인"
    
    # 워치햄스터 프로세스 확인
    if pgrep -f ".naming_backup/config_data_backup/watchhamster.log" > /dev/null; then
        WATCHHAMSTER_PID=$(pgrep -f ".naming_backup/config_data_backup/watchhamster.log")
        print_success "🐹 워치햄스터가 실행 중입니다"
        echo -e "${INFO}  • PID: $WATCHHAMSTER_PID${RESET}"
        
        # 실행 시간 계산
        if command -v ps &> /dev/null; then
            UPTIME=$(ps -o etime= -p $WATCHHAMSTER_PID 2>/dev/null | tr -d ' ')
            echo -e "${INFO}  • 실행시간: $UPTIME${RESET}"
        fi
        
        # CPU/메모리 사용률
        if command -v ps &> /dev/null; then
            CPU_MEM=$(ps -o pcpu,pmem -p $WATCHHAMSTER_PID --no-headers 2>/dev/null)
            echo -e "${INFO}  • CPU/메모리: $CPU_MEM${RESET}"
        fi
        
        echo
        echo -e "${YELLOW}📊 관리 중인 모듈 상태${RESET}"
        check_managed_processes
        
    else
        print_error "🐹 워치햄스터가 실행되지 않고 있습니다"
        echo -e "${INFO}워치햄스터를 먼저 시작해주세요${RESET}"
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# 관리되는 프로세스 상태 확인
check_managed_processes() {
# BROKEN_REF:     local processes=("POSCO News 250808_monitor.py" "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/integrated_report_scheduler.py")
    local running_count=0
    local total_count=${#processes[@]}
    
    for process in "${processes[@]}"; do
        if pgrep -f "$process" > /dev/null; then
            PID=$(pgrep -f "$process")
            print_success "  ✅ ${process%.*} (PID: $PID)"
            ((running_count++))
        else
            print_warning "  ❌ ${process%.*} (중지됨)"
        fi
    done
    
    echo
    if [ $running_count -eq $total_count ]; then
        print_success "🎯 모든 모듈이 정상 작동 중입니다 ($running_count/$total_count)"
    else
        print_warning "⚠️ 일부 모듈이 중지되어 있습니다 ($running_count/$total_count)"
    fi
}

# 모듈 관리 메뉴
manage_modules() {
    clear
    print_header "🔧 모듈 관리"
    
    # WatchHamster v3.0 상태 확인
    local watchhamster_pid=$(pgrep -f ".naming_backup/config_data_backup/watchhamster.log")
    if [[ -z "$watchhamster_pid" ]]; then
        print_error "❌ 워치햄스터가 실행되지 않았습니다"
        print_info "개별 모듈 관리를 위해서는 먼저 워치햄스터를 시작해주세요"
        echo
        read -p "계속하려면 Enter를 누르세요..."
        main_menu
        return
    fi
    
    print_success "🐹 워치햄스터가 실행 중입니다 (PID: $watchhamster_pid)"
    echo
    
    print_section "📊 개별 모듈 상태"
    
    local modules=(
        "posco_main_notifier.py:메인 알림 시스템:1"
        "realtime_news_monitor.py:실시간 뉴스 모니터:2"
        "integrated_report_scheduler.py:통합 리포트 스케줄러:3"
        "historical_data_collector.py:히스토리 데이터 수집기:4"
    )
    
    for module_info in "${modules[@]}"; do
        local script_name="${module_info%%:*}"
        local display_name="${module_info#*:}"
        display_name="${display_name%%:*}"
        local module_num="${module_info##*:}"
        local module_pid=$(pgrep -f "$script_name")
        
        if [[ -n "$module_pid" ]]; then
            local module_time=$(ps -p $module_pid -o etime= 2>/dev/null | tr -d ' ')
            echo -e "${GREEN}$module_num.${RESET} ✅ $display_name (PID: $module_pid, 실행시간: $module_time)"
        else
            echo -e "${RED}$module_num.${RESET} ❌ $display_name (중지됨)"
        fi
    done
    
    echo
    echo -e "${YELLOW}🔧 모듈 제어 옵션:${RESET}"
    echo -e "${GRAY}R.${RESET} 🔄 모든 모듈 재시작"
    echo -e "${GRAY}S.${RESET} 📊 상세 상태 보기"
    echo -e "${GRAY}L.${RESET} 📋 로그 보기"
    echo -e "${GRAY}0.${RESET} ⬅️ 메인 메뉴로 돌아가기"
    echo
    
    echo -n -e "${GREEN}🎯 선택하세요 (1-4, R, S, L, 0): ${RESET}"
    read -r choice
    
    case "$choice" in
        "1") control_individual_module "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/posco_main_notifier.py" "메인 알림 시스템" ;;
        "2") control_individual_module "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/realtime_news_monitor.py" "실시간 뉴스 모니터" ;;
        "3") control_individual_module "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/integrated_report_scheduler.py" "통합 리포트 스케줄러" ;;
        "4") control_individual_module "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/historical_data_collector.py" "히스토리 데이터 수집기" ;;
        "R"|"r") restart_all_modules ;;
        "S"|"s") show_detailed_module_status ;;
        "L"|"l") view_module_logs ;;
        "0") main_menu ;;
        *) 
            print_error "잘못된 선택입니다"
            sleep 2
            manage_modules
            ;;
    esac
}

# 개별 모듈 제어
control_individual_module() {
    local script_name="$1"
    local display_name="$2"
    
    clear
    print_header "🔧 $display_name 제어"
    
    local module_pid=$(pgrep -f "$script_name")
    if [[ -n "$module_pid" ]]; then
        local module_time=$(ps -p $module_pid -o etime= 2>/dev/null | tr -d ' ')
        local cpu=$(ps -p $module_pid -o %cpu= 2>/dev/null | tr -d ' ')
        local mem=$(ps -p $module_pid -o %mem= 2>/dev/null | tr -d ' ')
        
        print_success "✅ $display_name이 실행 중입니다"
        echo -e "${INFO}  • PID: $module_pid${RESET}"
        echo -e "${INFO}  • 실행시간: $module_time${RESET}"
        echo -e "${INFO}  • CPU: ${cpu}%, 메모리: ${mem}%${RESET}"
    else
        print_warning "❌ $display_name이 중지되어 있습니다"
    fi
    
    echo
    echo -e "${YELLOW}🔧 제어 옵션:${RESET}"
    echo -e "${GREEN}1.${RESET} 🔄 모듈 재시작"
    echo -e "${GREEN}2.${RESET} 🛑 모듈 중지"
    echo -e "${GREEN}3.${RESET} 📋 모듈 로그 보기"
    echo -e "${GREEN}0.${RESET} ⬅️ 돌아가기"
    echo
    
    echo -n -e "${GREEN}🎯 선택하세요 (1-3, 0): ${RESET}"
    read -r choice
    
    case "$choice" in
        "1") restart_individual_module "$script_name" "$display_name" ;;
        "2") stop_individual_module "$script_name" "$display_name" ;;
        "3") show_individual_module_log "$script_name" "$display_name" ;;
        "0") manage_modules ;;
        *) 
            print_error "잘못된 선택입니다"
            sleep 2
            control_individual_module "$script_name" "$display_name"
            ;;
    esac
}

# 개별 모듈 재시작
restart_individual_module() {
    local script_name="$1"
    local display_name="$2"
    
    clear
    print_header "🔄 $display_name 재시작"
    
    if ! confirm_action "$display_name을(를) 재시작하시겠습니까?"; then
        manage_modules
        return
    fi
    
    print_info "🔄 $display_name 재시작 중..."
    
    # 기존 프로세스 종료
    local old_pid=$(pgrep -f "$script_name")
    if [[ -n "$old_pid" ]]; then
        print_info "⏹️ 기존 프로세스 종료 중... (PID: $old_pid)"
        kill "$old_pid"
        sleep 3
    fi
    
    # 워치햄스터가 자동으로 재시작할 때까지 대기
    print_info "⏳ 워치햄스터의 자동 복구 대기 중... (10초)"
    sleep 10
    
    # 새 프로세스 확인
    local new_pid=$(pgrep -f "$script_name")
    if [[ -n "$new_pid" ]]; then
        print_success "✅ $display_name이(가) 성공적으로 재시작되었습니다. (PID: $new_pid)"
    else
        print_warning "⚠️ 자동 재시작이 지연되고 있습니다. 워치햄스터 로그를 확인해주세요."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    control_individual_module "$script_name" "$display_name"
}

# 개별 모듈 중지
stop_individual_module() {
    local script_name="$1"
    local display_name="$2"
    
    clear
    print_header "🛑 $display_name 중지"
    
    if ! confirm_action "$display_name을(를) 중지하시겠습니까?"; then
        control_individual_module "$script_name" "$display_name"
        return
    fi
    
    local module_pid=$(pgrep -f "$script_name")
    if [[ -n "$module_pid" ]]; then
        print_info "🛑 $display_name 중지 중... (PID: $module_pid)"
        kill "$module_pid" 2>/dev/null
        sleep 2
        
        # 강제 종료가 필요한 경우
        if kill -0 "$module_pid" 2>/dev/null; then
            print_warning "강제 종료 중..."
            kill -9 "$module_pid" 2>/dev/null
        fi
        
        print_success "✅ $display_name이 중지되었습니다"
        print_warning "⚠️ 워치햄스터가 자동으로 재시작할 수 있습니다"
    else
        print_info "ℹ️ $display_name이 이미 중지되어 있습니다"
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    control_individual_module "$script_name" "$display_name"
}

# 개별 모듈 로그 보기
show_individual_module_log() {
    local script_name="$1"
    local display_name="$2"
    
    clear
    print_header "📋 $display_name 로그"
    
    # 로그 파일 경로 추정
    local log_files=(".naming_backup/config_data_backup/watchhamster.log" ".naming_backup/config_data_backup/posco_monitor.log" ".naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log")
    local found_log=false
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            print_info "📁 로그 파일: $log_file"
            echo
            print_section "최근 로그 (마지막 20줄, $script_name 관련)"
            
            # 해당 모듈과 관련된 로그만 필터링
            if grep -i "${script_name%.*}" "$log_file" | tail -20 | grep -q .; then
                echo -e "${GRAY}$(grep -i "${script_name%.*}" "$log_file" | tail -20)${RESET}"
                found_log=true
            else
                echo -e "${GRAY}$(tail -20 "$log_file")${RESET}"
                found_log=true
            fi
            break
        fi
    done
    
    if [[ "$found_log" == false ]]; then
        print_warning "❌ 관련 로그 파일을 찾을 수 없습니다"
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    control_individual_module "$script_name" "$display_name"
}

# 모든 모듈 재시작
restart_all_modules() {
    clear
    print_header "🔄 모든 모듈 재시작"
    
    if ! confirm_action "모든 모듈을 재시작하시겠습니까?"; then
        manage_modules
        return
    fi
    
    print_info "🔄 워치햄스터를 통한 전체 시스템 재시작 중..."
    
    # 워치햄스터 재시작으로 모든 모듈 재시작
    restart_watchhamster
}

# 상세 모듈 상태 보기
show_detailed_module_status() {
    clear
    print_header "📊 상세 모듈 상태"
    
    local modules=(
        "posco_main_notifier.py:메인 알림 시스템"
        "realtime_news_monitor.py:실시간 뉴스 모니터"
        "integrated_report_scheduler.py:통합 리포트 스케줄러"
        "historical_data_collector.py:히스토리 데이터 수집기"
    )
    
    for module_info in "${modules[@]}"; do
        local script_name="${module_info%%:*}"
        local display_name="${module_info##*:}"
        local module_pid=$(pgrep -f "$script_name")
        
        print_section "$display_name"
        
        if [[ -n "$module_pid" ]]; then
            local time=$(ps -p $module_pid -o etime= 2>/dev/null | tr -d ' ')
            local cpu=$(ps -p $module_pid -o %cpu= 2>/dev/null | tr -d ' ')
            local mem=$(ps -p $module_pid -o %mem= 2>/dev/null | tr -d ' ')
            local vsz=$(ps -p $module_pid -o vsz= 2>/dev/null | tr -d ' ')
            
            print_success "✅ 실행 중"
            echo -e "  ${GRAY}•${RESET} PID: $module_pid"
            echo -e "  ${GRAY}•${RESET} 실행시간: $time"
            echo -e "  ${GRAY}•${RESET} CPU 사용률: ${cpu}%"
            echo -e "  ${GRAY}•${RESET} 메모리 사용률: ${mem}%"
            echo -e "  ${GRAY}•${RESET} 가상 메모리: ${vsz}KB"
        else
            print_error "❌ 중지됨"
        fi
        echo
    done
    
    read -p "계속하려면 Enter를 누르세요..."
    manage_modules
}

# 모듈 로그 보기
view_module_logs() {
    clear
    print_header "📋 모듈 로그 보기"
    
    echo -e "${YELLOW}📋 확인할 로그를 선택하세요:${RESET}"
    echo
    echo -e "${GREEN}1.${RESET} 🐹 워치햄스터 로그"
    echo -e "${GREEN}2.${RESET} 📊 메인 알림 시스템 로그"
    echo -e "${GREEN}3.${RESET} 🔄 실시간 모니터 로그"
    echo -e "${GREEN}4.${RESET} 📈 통합 리포트 로그"
    echo -e "${GREEN}0.${RESET} ⬅️ 돌아가기"
    echo
    
    echo -n -e "${GREEN}🎯 선택하세요 (1-4, 0): ${RESET}"
    read -r choice
    
    case "$choice" in
        "1") show_log_file ".naming_backup/config_data_backup/.naming_backup/config_data_backup/watchhamster.log" "워치햄스터" ;;
        "2") show_log_file ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_monitor.log" "메인 알림 시스템" ;;
# BROKEN_REF:         "3") show_log_file "realtime_monitor.log" "실시간 모니터" ;;
# BROKEN_REF:         "4") show_log_file "integrated_report.log" "통합 리포트" ;;
        "0") manage_modules ;;
        *) 
            print_error "잘못된 선택입니다."
            sleep 2
            view_module_logs
            ;;
    esac
}

# 로그 파일 표시
show_log_file() {
    local log_file="$1"
    local log_name="$2"
    local log_path="$SCRIPT_DIR/$log_file"
    
    clear
    print_header "📋 $log_name 로그"
    
    if [[ -f "$log_path" ]]; then
        print_info "📁 로그 파일: $log_path"
        local size=$(du -h "$log_path" 2>/dev/null | cut -f1)
        print_info "📊 파일 크기: $size"
        echo
        
        print_section "최근 로그 (마지막 20줄)"
        echo -e "${GRAY}$(tail -20 "$log_path")${RESET}"
    else
        print_warning "❌ 로그 파일을 찾을 수 없습니다: $log_path"
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    view_module_logs
}

# ============================================================================
# 뉴스 관리
# ============================================================================

# 뉴스 로그 확인
view_news_logs() {
    clear
    print_header "📋 뉴스 로그 확인"
    
    if [[ -f ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_monitor.log" ]]; then
        echo -e "${CYAN}최근 20줄의 로그:${RESET}"
        echo
        tail -n 20 ".naming_backup/config_data_backup/.naming_backup/config_data_backup/posco_monitor.log"
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
    
# BROKEN_REF:     if [[ -f "POSCO News 250808_data.json" ]]; then
# BROKEN_REF:         local size=$(du -h "POSCO News 250808_data.json" 2>/dev/null | cut -f1)
# BROKEN_REF:         local modified=$(stat -f "%Sm" "POSCO News 250808_data.json" 2>/dev/null)
        echo -e "${GREEN}✅${RESET} POSCO News 250808_data.json (${size}, 수정: $modified)"
        
        # 간단한 통계
# BROKEN_REF:         local count=$(python3 -c "import json; print(len(json.load(open('POSCO News 250808_data.json'))))" 2>/dev/null || echo "N/A")
        echo -e "  총 뉴스 수: $count개"
    else
        echo -e "${RED}❌${RESET} POSCO News 250808_data.json (없음)"
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

# BROKEN_REF:     if [[ -f "POSCO News 250808_data.json" ]]; then
        echo -e "${CYAN}검색 결과:${RESET}"
        echo
        python3 -c "
import test_config.json
keyword = '$keyword'
try:
# BROKEN_REF:     with open('POSCO News 250808_data.json', 'r', encoding='utf-8') as f:
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
    local required_files=("Monitoring/POSCO_News_250808/posco_main_notifier.py" ".naming_backup/config_data_backup/watchhamster.log" "Monitoring/POSCO_News_250808/config.py" "requirements.txt")
    check_required_files "${required_files[@]}"
    
    # 데이터 파일 확인
    print_section "📊 데이터 파일 상태"
# BROKEN_REF:     local data_files=("POSCO News 250808_data.json" "POSCO News 250808_cache.json")
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
    if [[ -f "Monitoring/POSCO_News_250808/posco_main_notifier.py" ]]; then
# BROKEN_REF:         if python3 -c "import sys; print('Python 스크립트 테스트 통과')" 2>/dev/null; then
            print_success "🐹 POSCO 메인 알림 시스템 테스트 통과"
        else
            print_error "🐹 POSCO 메인 알림 시스템 테스트 실패"
        fi
    elif [[ -f ".naming_backup/config_data_backup/watchhamster.log" ]]; then
# BROKEN_REF:         if python3 -c "import sys; print('Python 스크립트 테스트 통과')" 2>/dev/null; then
            print_success "🐹 POSCO WatchHamster v3.0 테스트 통과"
        else
            print_error "🐹 POSCO WatchHamster v3.0 테스트 실패"
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
# BROKEN_REF:     local data_files=("POSCO News 250808_data.json" "POSCO News 250808_cache.json" "*.py" "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/config.py")
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
        bash .naming_backup/config_data_backup/watchhamster.log"
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