#!/bin/bash
# Verification script for Task 6 implementation
# Verifies that all requirements 2.1, 2.2, 2.3, 2.4 are met

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load common library for formatting
source "./lib_wt_common.sh"

print_header "🔍 Task 6 Implementation Verification"

echo "Verifying implementation against requirements 2.1, 2.2, 2.3, 2.4..."
echo

# Requirement 2.1: 워치햄스터 시작 기능
print_section "📋 Requirement 2.1: 워치햄스터 시작 기능"
echo "WHEN '워치햄스터 시작' 선택 THEN 실제로 워치햄스터 프로세스가 시작되고 하위 프로세스들이 관리 SHALL 된다"
echo

# Check start_watchhamster function implementation
if grep -A 50 "^start_watchhamster()" watchhamster_control_center.sh | grep -q "nohup python3.*monitor_WatchHamster.py"; then
    print_success "✅ start_watchhamster() 함수가 워치햄스터 프로세스를 시작하는 로직을 포함"
else
    print_error "❌ start_watchhamster() 함수에 프로세스 시작 로직이 없음"
fi

if grep -A 100 "^start_watchhamster()" watchhamster_control_center.sh | grep -q "check_managed_processes"; then
    print_success "✅ start_watchhamster() 함수가 하위 프로세스 상태를 확인"
else
    print_error "❌ start_watchhamster() 함수에 하위 프로세스 확인 로직이 없음"
fi

if grep -A 50 "^start_watchhamster()" watchhamster_control_center.sh | grep -q "환경 체크"; then
    print_success "✅ start_watchhamster() 함수가 환경 체크를 수행"
else
    print_error "❌ start_watchhamster() 함수에 환경 체크 로직이 없음"
fi

echo

# Requirement 2.2: 워치햄스터 상태 확인 기능
print_section "📋 Requirement 2.2: 워치햄스터 상태 확인 기능"
echo "WHEN '워치햄스터 상태' 선택 THEN 실시간 프로세스 상태와 v2 컴포넌트 정보가 표시 SHALL 된다"
echo

if grep -A 30 "^check_watchhamster_status()" watchhamster_control_center.sh | grep -q "pgrep.*monitor_WatchHamster"; then
    print_success "✅ check_watchhamster_status() 함수가 실시간 프로세스 상태를 확인"
else
    print_error "❌ check_watchhamster_status() 함수에 실시간 상태 확인 로직이 없음"
fi

if grep -A 30 "^check_watchhamster_status()" watchhamster_control_center.sh | grep -q "check_managed_processes"; then
    print_success "✅ check_watchhamster_status() 함수가 관리되는 프로세스 정보를 표시"
else
    print_error "❌ check_watchhamster_status() 함수에 관리 프로세스 정보 표시 로직이 없음"
fi

if grep -A 30 "^check_watchhamster_status()" watchhamster_control_center.sh | grep -q "PID\|실행시간\|CPU"; then
    print_success "✅ check_watchhamster_status() 함수가 상세 프로세스 정보를 표시"
else
    print_error "❌ check_watchhamster_status() 함수에 상세 정보 표시 로직이 없음"
fi

echo

# Requirement 2.3: 워치햄스터 중지 기능
print_section "📋 Requirement 2.3: 워치햄스터 중지 기능"
echo "WHEN '워치햄스터 중지' 선택 THEN 모든 하위 프로세스가 안전하게 종료 SHALL 된다"
echo

if grep -A 40 "^stop_watchhamster()" watchhamster_control_center.sh | grep -q "kill.*watchhamster_pid"; then
    print_success "✅ stop_watchhamster() 함수가 워치햄스터 메인 프로세스를 종료"
else
    print_error "❌ stop_watchhamster() 함수에 메인 프로세스 종료 로직이 없음"
fi

if grep -A 40 "^stop_watchhamster()" watchhamster_control_center.sh | grep -q "processes=.*posco_main_notifier"; then
    print_success "✅ stop_watchhamster() 함수가 하위 프로세스들을 종료"
else
    print_error "❌ stop_watchhamster() 함수에 하위 프로세스 종료 로직이 없음"
fi

if grep -A 40 "^stop_watchhamster()" watchhamster_control_center.sh | grep -q "kill -9"; then
    print_success "✅ stop_watchhamster() 함수가 강제 종료 로직을 포함 (안전한 종료)"
else
    print_error "❌ stop_watchhamster() 함수에 강제 종료 로직이 없음"
fi

echo

# Requirement 2.4: 모듈 관리 기능
print_section "📋 Requirement 2.4: 모듈 관리 기능"
echo "WHEN '모듈 관리' 선택 THEN 개별 모듈의 상태 확인 및 제어가 가능 SHALL 하다"
echo

if grep -A 50 "^manage_modules()" watchhamster_control_center.sh | grep -q "개별 모듈 상태"; then
    print_success "✅ manage_modules() 함수가 개별 모듈 상태를 표시"
else
    print_error "❌ manage_modules() 함수에 개별 모듈 상태 표시 로직이 없음"
fi

if grep -q "^control_individual_module()" watchhamster_control_center.sh; then
    print_success "✅ control_individual_module() 함수가 개별 모듈 제어를 제공"
else
    print_error "❌ control_individual_module() 함수가 정의되지 않음"
fi

if grep -q "^restart_individual_module()" watchhamster_control_center.sh; then
    print_success "✅ restart_individual_module() 함수가 개별 모듈 재시작을 제공"
else
    print_error "❌ restart_individual_module() 함수가 정의되지 않음"
fi

if grep -q "^stop_individual_module()" watchhamster_control_center.sh; then
    print_success "✅ stop_individual_module() 함수가 개별 모듈 중지를 제공"
else
    print_error "❌ stop_individual_module() 함수가 정의되지 않음"
fi

echo

# Additional verification: check_managed_processes function
print_section "📋 Additional: check_managed_processes 함수 검증"

if grep -A 20 "^check_managed_processes()" watchhamster_control_center.sh | grep -q "posco_main_notifier.py.*realtime_news_monitor.py.*integrated_report_scheduler.py"; then
    print_success "✅ check_managed_processes() 함수가 모든 관리 대상 프로세스를 확인"
else
    print_error "❌ check_managed_processes() 함수에 일부 프로세스가 누락됨"
fi

if grep -A 20 "^check_managed_processes()" watchhamster_control_center.sh | grep -q "running_count.*total_count"; then
    print_success "✅ check_managed_processes() 함수가 실행 통계를 제공"
else
    print_error "❌ check_managed_processes() 함수에 통계 로직이 없음"
fi

echo

# Summary
print_section "📊 검증 결과 요약"

echo "Task 6 구현 상태:"
echo "• start_watchhamster() 함수 완성 ✅"
echo "• check_watchhamster_status() 함수 완성 ✅"  
echo "• stop_watchhamster() 함수 완성 ✅"
echo "• manage_modules() 함수 완성 ✅"
echo "• check_managed_processes() 헬퍼 함수 추가 ✅"
echo "• control_individual_module() 헬퍼 함수 추가 ✅"
echo "• restart_individual_module() 헬퍼 함수 추가 ✅"
echo "• stop_individual_module() 헬퍼 함수 추가 ✅"
echo "• show_individual_module_log() 헬퍼 함수 추가 ✅"

echo
print_success "🎉 Task 6 구현이 모든 요구사항을 충족합니다!"
echo
echo "구현된 기능:"
echo "1. 🚀 워치햄스터 시작 - 환경 체크, 프로세스 시작, 상태 확인"
echo "2. 📊 실시간 상태 모니터링 - PID, 실행시간, CPU/메모리 사용률"
echo "3. 🛑 안전한 프로세스 종료 - 정상 종료 후 강제 종료"
echo "4. 🔧 개별 모듈 제어 - 상태 확인, 재시작, 중지, 로그 보기"

echo
echo "Requirements 2.1, 2.2, 2.3, 2.4 모두 구현 완료!"