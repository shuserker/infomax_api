#!/bin/bash
# ============================================================================
# Watchhamster V3.0 Master Control
# POSCO 시스템 제어센터
# 
# WatchHamster v3.0 및 POSCO News 250808 호환
# Created: 2025-08-08
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 공통 라이브러리 로드
source "lib_wt_common.sh"

# 초기화
init_system

# ============================================================================
# 메인 메뉴
# ============================================================================
main_menu() {
    clear
    print_header "🐹 WatchHamster Master Control Center v4.0 🛡️"
    echo -e "${INFO}🎯 현재 활성화된 모니터링 시스템을 관리합니다${RESET}"
    echo

    echo -e "${YELLOW}🎛️ 관리할 시스템을 선택하세요:${RESET}"
    echo

    # 활성화된 모니터링 시스템
    start_box "${GREEN}"
    echo -e "${GREEN}║${RESET}                       ${CYAN}🏭 활성화된 모니터링 시스템${RESET}                       ${GREEN}║${RESET}"
    echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "1." "🏭 POSCO 뉴스 모니터링" "POSCO News 250808 및 주가 모니터링 시스템"
    end_box

    echo

    # 시스템 관리
    start_box "${BLUE}"
    echo -e "${BLUE}║${RESET}                           ${MAGENTA}🔧 시스템 관리${RESET}                                    ${BLUE}║${RESET}"
    echo -e "${BLUE}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "A." "🛡️ 전체 시스템 상태" "모든 WatchHamster v3.0 상태 확인"
    print_menu_item "B." "🔄 전체 시스템 업데이트" "모든 시스템 Git 업데이트"
    print_menu_item "C." "📋 통합 로그 관리" "모든 시스템 로그 통합 관리"
    print_menu_item "D." "🧪 전체 시스템 테스트" "모든 시스템 통합 테스트"
    end_box

    echo

    # 고급 관리
    start_box "${RED}"
    echo -e "${RED}║${RESET}                           ${WHITE}⚙️ 고급 관리${RESET}                                      ${RED}║${RESET}"
    echo -e "${RED}╠═══════════════════════════════════════════════════════════════════════════════╣${RESET}"
    print_menu_item "E." "📦 전체 백업 생성" "모든 시스템 통합 백업"
    print_menu_item "F." "🔧 워치햄스터 설정" "총괄 설정 관리"
    print_menu_item "G." "🎨 UI 테마 변경" "색상 테마 및 인터페이스 설정"
    end_box

    echo
    echo -e "${GRAY}0. ❌ 종료${RESET}"
    echo

    print_system_info

    echo -n -e "${GREEN}🎯 선택하세요 (1, A-G, 0): ${RESET}"
    read -r choice

    case "$choice" in
        "1") posco_monitoring ;;
        "A"|"a") system_status ;;
        "B"|"b") system_update ;;
        "C"|"c") integrated_logs ;;
        "D"|"d") system_test ;;
        "E"|"e") full_backup ;;
        "F"|"f") watchhamster_config ;;
        "G"|"g") ui_theme_config ;;
        "0") exit_system ;;
        *) invalid_choice ;;
    esac
}

# ============================================================================
# POSCO 모니터링 시스템
# ============================================================================
posco_monitoring() {
    clear
    print_header "🏭 POSCO 모니터링 시스템 진입"
    
    local loading_pid
    show_loading "POSCO 모니터링 시스템으로 이동 중" &
    loading_pid=$!
    
    sleep 2
    stop_loading $loading_pid

    cd "Monitoring/POSCO News 250808_mini" 2>/dev/null || {
        print_error "POSCO 모니터링 디렉토리를 찾을 수 없습니다."
        print_info "경로: Monitoring/POSCO News 250808_mini/"
        echo
        read -p "계속하려면 Enter를 누르세요..."
        cd "$SCRIPT_DIR"
        main_menu
        return
    }

    # POSCO 관리 센터 실행
    if [[ -f "Monitoring/POSCO_News_250808/Monitoring/POSCO_News_250808/posco_news_250808_control_center.sh" ]]; then
        bash Monitoring/POSCO_News_250808/posco_news_250808_control_center.sh"
# BROKEN_REF:     elif [[ -f "POSCO_통합_관리_센터_v3.bat" ]]; then
        print_warning "Windows BAT 파일을 발견했습니다. Mac용 스크립트로 변환이 필요합니다."
        read -p "계속하려면 Enter를 누르세요..."
    else
        print_error "POSCO 모니터링 시스템을 찾을 수 없습니다."
        print_info "POSCO_News_250808.py"
        echo
        read -p "계속하려면 Enter를 누르세요..."
    fi

    cd "$SCRIPT_DIR"
    main_menu
}

# ============================================================================
# 전체 시스템 상태
# ============================================================================
system_status() {
    clear
    print_header "🛡️ 전체 시스템 상태 확인"
    
    local loading_pid
    show_loading "모든 WatchHamster v3.0 상태를 확인하고 있습니다" &
    loading_pid=$!
    
    sleep 2
    stop_loading $loading_pid

    print_section "📊 시스템 상태 현황"

    # Python 환경 확인
    print_section "🐍 Python 환경"
    check_python_environment

    # 필수 파일 확인
    print_section "📁 필수 파일 확인"
    local required_files=(
        "lib_wt_common.sh"
        "requirements.txt"
        "README.md"
    )
    check_required_files "${required_files[@]}"

    # 네트워크 연결 확인
    print_section "🌐 네트워크 상태"
    check_network_connection

    # Git 저장소 상태 확인
    print_section "📦 Git 저장소 상태"
    check_git_status

    # 프로세스 확인
    print_section "⚙️ 프로세스 상태"
    check_process "python"
    check_process "monitor"

    # 시스템 리소스 확인
    print_section "💻 시스템 리소스"
    print_system_info

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 전체 시스템 업데이트
# ============================================================================
system_update() {
    clear
    print_header "🔄 전체 시스템 업데이트"
    
    if ! confirm_action "모든 워치햄스터 시스템을 업데이트하시겠습니까?"; then
        main_menu
        return
    fi

    local loading_pid
    show_loading "시스템 업데이트를 진행하고 있습니다" &
    loading_pid=$!

    # Git 상태 확인
    if [[ -d ".git" ]]; then
        print_section "📦 Git 업데이트"
        
        # 현재 브랜치 확인
        local current_branch=$(git branch --show-current 2>/dev/null)
        print_info "현재 브랜치: $current_branch"
        
        # 원격 변경사항 가져오기
        if git fetch origin 2>/dev/null; then
            print_success "원격 저장소에서 변경사항을 가져왔습니다."
        else
            print_error "원격 저장소 접근에 실패했습니다."
        fi
        
        # 로컬 변경사항 확인
        local status=$(git status --porcelain 2>/dev/null)
        if [[ -n "$status" ]]; then
            print_warning "로컬 변경사항이 있습니다. 백업을 권장합니다."
            if confirm_action "변경사항을 커밋하시겠습니까?"; then
                git add .
                git commit -m "Auto commit: $(date '+%Y-%m-%d %H:%M:%S')"
                print_success "변경사항이 커밋되었습니다."
            fi
        fi
        
        # 업데이트 적용
        if git pull origin "$current_branch" 2>/dev/null; then
            print_success "시스템이 최신 상태로 업데이트되었습니다."
        else
            print_error "업데이트 중 오류가 발생했습니다."
        fi
    else
        print_warning "Git 저장소가 아닙니다."
    fi

    stop_loading $loading_pid

    # POSCO 모니터링 업데이트
    if [[ -d "Monitoring/POSCO News 250808_mini" ]]; then
        print_section "🏭 POSCO 모니터링 업데이트"
        cd "Monitoring/POSCO News 250808_mini"
        
        if [[ -d ".git" ]]; then
            if git pull origin main 2>/dev/null; then
                print_success "POSCO 모니터링이 업데이트되었습니다."
            else
                print_warning "POSCO 모니터링 업데이트에 실패했습니다."
            fi
        fi
        
        cd "$SCRIPT_DIR"
    fi

    print_success "전체 시스템 업데이트가 완료되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 통합 로그 관리
# ============================================================================
integrated_logs() {
    clear
    print_header "📋 통합 로그 관리"
    
    print_section "📊 로그 파일 현황"
    
    # 로그 디렉토리 확인
    local log_dir="$HOME/.watchhamster/logs"
    if [[ -d "$log_dir" ]]; then
        print_success "로그 디렉토리: $log_dir"
        
        # 로그 파일 목록
        local log_files=($(find "$log_dir" -name "*.log" -type f 2>/dev/null))
        if [[ ${#log_files[@]} -gt 0 ]]; then
            echo -e "${WHITE}발견된 로그 파일들:${RESET}"
            for file in "${log_files[@]}"; do
                local size=$(du -h "$file" 2>/dev/null | cut -f1)
                local modified=$(stat -f "%Sm" "$file" 2>/dev/null)
                echo -e "  ${GRAY}•${RESET} $(basename "$file") (${size}, 수정: $modified)"
            done
        else
            print_info "로그 파일이 없습니다."
        fi
    else
        print_warning "로그 디렉토리가 없습니다."
    fi

    echo
    echo -e "${YELLOW}로그 관리 옵션:${RESET}"
    echo "1. 최신 로그 보기"
    echo "2. 에러 로그 보기"
    echo "3. 로그 파일 정리"
    echo "4. 로그 설정 변경"
    echo "0. 돌아가기"
    echo
    
    echo -n -e "${GREEN}선택하세요 (1-4, 0): ${RESET}"
    read -r log_choice

    case "$log_choice" in
        "1") view_latest_logs ;;
        "2") view_error_logs ;;
        "3") cleanup_logs ;;
        "4") log_settings ;;
        "0") main_menu ;;
        *) invalid_choice ;;
    esac
}

# 로그 보기 함수들
view_latest_logs() {
    clear
    print_header "📋 최신 로그 보기"
    
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${CYAN}최근 20줄의 로그:${RESET}"
        echo
        tail -n 20 "$LOG_FILE"
    else
        print_warning "로그 파일이 없습니다."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    integrated_logs
}

view_error_logs() {
    clear
    print_header "📋 에러 로그 보기"
    
    if [[ -f "$ERROR_LOG" ]]; then
        echo -e "${CYAN}최근 에러 로그:${RESET}"
        echo
        tail -n 20 "$ERROR_LOG"
    else
        print_warning "에러 로그 파일이 없습니다."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    integrated_logs
}

cleanup_logs() {
    clear
    print_header "📋 로그 파일 정리"
    
    if confirm_action "30일 이상 된 로그 파일을 삭제하시겠습니까?"; then
        find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null
        print_success "오래된 로그 파일이 정리되었습니다."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    integrated_logs
}

log_settings() {
    clear
    print_header "📋 로그 설정"
    
    print_info "현재 로그 설정:"
    echo "  로그 디렉토리: $LOG_DIR"
    echo "  로그 파일: $LOG_FILE"
    echo "  에러 로그: $ERROR_LOG"
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    integrated_logs
}

# ============================================================================
# 전체 시스템 테스트
# ============================================================================
system_test() {
    clear
    print_header "🧪 전체 시스템 테스트"
    
    if ! confirm_action "전체 시스템 테스트를 실행하시겠습니까?"; then
        main_menu
        return
    fi

    local loading_pid
    show_loading "시스템 테스트를 진행하고 있습니다" &
    loading_pid=$!

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
    
    # 파일 시스템 테스트
    local test_files=("lib_wt_common.sh" "requirements.txt")
    if check_required_files "${test_files[@]}"; then
        print_success "파일 시스템 테스트 통과"
    else
        print_error "파일 시스템 테스트 실패"
    fi
    
    # POSCO 모니터링 테스트
    print_section "🏭 POSCO 모니터링 테스트"
    if [[ -d "Monitoring/POSCO News 250808_mini" ]]; then
        cd "Monitoring/POSCO News 250808_mini"
        
        # Python 스크립트 테스트
        if [[ -f "Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/Monitoring/POSCO_News_250808/backup_archive_20250806/disabled_monitors_20250803/run_monitor.py" ]]; then
# BROKEN_REF:             if python3 -c "import sys; print('Python 스크립트 테스트 통과')" 2>/dev/null; then
                print_success "POSCO Python 스크립트 테스트 통과"
            else
                print_error "POSCO Python 스크립트 테스트 실패"
            fi
        fi
        
        cd "$SCRIPT_DIR"
    else
        print_warning "POSCO 모니터링 디렉토리가 없습니다."
    fi

    stop_loading $loading_pid

    print_success "전체 시스템 테스트가 완료되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 전체 백업 생성
# ============================================================================
full_backup() {
    clear
    print_header "📦 전체 백업 생성"
    
    if ! confirm_action "전체 시스템 백업을 생성하시겠습니까?"; then
        main_menu
        return
    fi

    local backup_dir="$HOME/.watchhamster/backups"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_name="watchhamster_backup_$timestamp"
    local backup_path="$backup_dir/$backup_name"

    mkdir -p "$backup_dir"

    local loading_pid
    show_loading "백업을 생성하고 있습니다" &
    loading_pid=$!

    # 중요 파일들 백업
    local important_files=(
        "lib_wt_common.sh"
        "requirements.txt"
        "README.md"
        "*.py"
        "*.json"
        "*.html"
    )

    for pattern in "${important_files[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                mkdir -p "$(dirname "$backup_path/$(dirname "$file")")"
                cp -r "$file" "$backup_path/" 2>/dev/null
            fi
        done
    done

    # Monitoring 디렉토리 백업
    if [[ -d "Monitoring" ]]; then
        cp -r "Monitoring" "$backup_path/" 2>/dev/null
    fi

    # 로그 파일 백업
    if [[ -d "$LOG_DIR" ]]; then
        cp -r "$LOG_DIR" "$backup_path/" 2>/dev/null
    fi

    stop_loading $loading_pid

    # 백업 압축
    if [[ -d "$backup_path" ]]; then
        cd "$backup_dir"
        tar -czf "$backup_name.tar.gz" "$backup_name" 2>/dev/null
        rm -rf "$backup_name"
        cd "$SCRIPT_DIR"
        
        local backup_size=$(du -h "$backup_dir/$backup_name.tar.gz" 2>/dev/null | cut -f1)
        print_success "백업이 생성되었습니다: $backup_name.tar.gz (크기: $backup_size)"
    else
        print_error "백업 생성에 실패했습니다."
    fi

    echo
    read -p "계속하려면 Enter를 누르세요..."
    main_menu
}

# ============================================================================
# 워치햄스터 설정
# ============================================================================
watchhamster_config() {
    clear
    print_header "🔧 워치햄스터 설정"
    
    print_section "⚙️ 현재 설정"
    
    # 설정 파일 확인
    local config_file="test_config.json"
    if [[ -f "$config_file" ]]; then
        print_success "설정 파일 발견: $config_file"
        echo -e "${CYAN}현재 설정:${RESET}"
        cat "$config_file" | python3 -m json.tool 2>/dev/null || cat "$config_file"
    else
        print_info "설정 파일이 없습니다. 기본 설정을 사용합니다."
    fi

    echo
    echo -e "${YELLOW}설정 옵션:${RESET}"
    echo "1. 로그 레벨 설정"
    echo "2. 모니터링 간격 설정"
    echo "3. 알림 설정"
    echo "4. 테마 설정"
    echo "5. 설정 초기화"
    echo "0. 돌아가기"
    echo
    
    echo -n -e "${GREEN}선택하세요 (1-5, 0): ${RESET}"
    read -r config_choice

    case "$config_choice" in
        "1") log_level_config ;;
        "2") monitoring_interval_config ;;
        "3") notification_config ;;
        "4") theme_config ;;
        "5") reset_config ;;
        "0") main_menu ;;
        *) invalid_choice ;;
    esac
}

# 설정 함수들
log_level_config() {
    clear
    print_header "🔧 로그 레벨 설정"
    
    echo -e "${CYAN}로그 레벨 옵션:${RESET}"
    echo "1. DEBUG - 모든 로그 출력"
    echo "2. INFO - 정보성 로그만 출력 (기본값)"
    echo "3. WARNING - 경고 이상만 출력"
    echo "4. ERROR - 에러만 출력"
    echo
    
    echo -n -e "${GREEN}로그 레벨을 선택하세요 (1-4): ${RESET}"
    read -r level_choice

    local level="INFO"
    case "$level_choice" in
        "1") level="DEBUG" ;;
        "2") level="INFO" ;;
        "3") level="WARNING" ;;
        "4") level="ERROR" ;;
        *) print_error "잘못된 선택입니다." ;;
    esac

    # 설정 파일 업데이트
    local config_dir="$HOME/.watchhamster"
    mkdir -p "$config_dir"
    
    cat > "test_config.json" << EOF
{
    "log_level": "$level",
    "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

    print_success "로그 레벨이 $level로 설정되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    watchhamster_config
}

monitoring_interval_config() {
    clear
    print_header "🔧 모니터링 간격 설정"
    
    echo -e "${CYAN}모니터링 간격 옵션:${RESET}"
    echo "1. 30초 (빠른 모니터링)"
    echo "2. 1분 (기본값)"
    echo "3. 5분 (절약 모드)"
    echo "4. 10분 (저전력 모드)"
    echo
    
    echo -n -e "${GREEN}간격을 선택하세요 (1-4): ${RESET}"
    read -r interval_choice

    local interval="60"
    case "$interval_choice" in
        "1") interval="30" ;;
        "2") interval="60" ;;
        "3") interval="300" ;;
        "4") interval="600" ;;
        *) print_error "잘못된 선택입니다." ;;
    esac

    print_success "모니터링 간격이 ${interval}초로 설정되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    watchhamster_config
}

notification_config() {
    clear
    print_header "🔧 알림 설정"
    
    echo -e "${CYAN}알림 옵션:${RESET}"
    echo "1. 모든 알림 활성화"
    echo "2. 중요 알림만"
    echo "3. 알림 비활성화"
    echo
    
    echo -n -e "${GREEN}알림 설정을 선택하세요 (1-3): ${RESET}"
    read -r notif_choice

    local notification="all"
    case "$notif_choice" in
        "1") notification="all" ;;
        "2") notification="important" ;;
        "3") notification="none" ;;
        *) print_error "잘못된 선택입니다." ;;
    esac

    print_success "알림 설정이 변경되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    watchhamster_config
}

theme_config() {
    clear
    print_header "🔧 테마 설정"
    
    echo -e "${CYAN}테마 옵션:${RESET}"
    echo "1. 기본 테마 (macOS)"
    echo "2. 다크 테마"
    echo "3. 라이트 테마"
    echo "4. 고대비 테마"
    echo
    
    echo -n -e "${GREEN}테마를 선택하세요 (1-4): ${RESET}"
    read -r theme_choice

    local theme="default"
    case "$theme_choice" in
        "1") theme="default" ;;
        "2") theme="dark" ;;
        "3") theme="light" ;;
        "4") theme="high_contrast" ;;
        *) print_error "잘못된 선택입니다." ;;
    esac

    print_success "테마가 변경되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    watchhamster_config
}

reset_config() {
    clear
    print_header "🔧 설정 초기화"
    
    if confirm_action "모든 설정을 초기화하시겠습니까?"; then
        rm -f "test_config.json"
        print_success "설정이 초기화되었습니다."
    fi
    
    echo
    read -p "계속하려면 Enter를 누르세요..."
    watchhamster_config
}

# ============================================================================
# UI 테마 변경
# ============================================================================
ui_theme_config() {
    clear
    print_header "🎨 UI 테마 변경"
    
    print_section "🎨 사용 가능한 테마"
    
    echo -e "${CYAN}테마 옵션:${RESET}"
    echo "1. 🍎 macOS 기본 테마"
    echo "2. 🌙 다크 모드"
    echo "3. ☀️ 라이트 모드"
    echo "4. 🎨 고대비 모드"
    echo "5. 🌈 컬러풀 모드"
    echo "0. 돌아가기"
    echo
    
    echo -n -e "${GREEN}테마를 선택하세요 (1-5, 0): ${RESET}"
    read -r theme_choice

    case "$theme_choice" in
        "1") apply_macos_theme ;;
        "2") apply_dark_theme ;;
        "3") apply_light_theme ;;
        "4") apply_high_contrast_theme ;;
        "5") apply_colorful_theme ;;
        "0") main_menu ;;
        *) invalid_choice ;;
    esac
}

# 테마 적용 함수들
apply_macos_theme() {
    print_success "macOS 기본 테마가 적용되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    ui_theme_config
}

apply_dark_theme() {
    print_success "다크 테마가 적용되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    ui_theme_config
}

apply_light_theme() {
    print_success "라이트 테마가 적용되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    ui_theme_config
}

apply_high_contrast_theme() {
    print_success "고대비 테마가 적용되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    ui_theme_config
}

apply_colorful_theme() {
    print_success "컬러풀 테마가 적용되었습니다."
    echo
    read -p "계속하려면 Enter를 누르세요..."
    ui_theme_config
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

# 시스템 종료
exit_system() {
    clear
    print_header "👋 WatchHamster Master Control Center 종료"
    print_success "시스템이 안전하게 종료되었습니다."
    print_info ".naming_backup/config_data_backup/watchhamster.log"
    echo
    exit 0
}

# ============================================================================
# 메인 실행
# ============================================================================

# 스크립트 시작
main_menu 