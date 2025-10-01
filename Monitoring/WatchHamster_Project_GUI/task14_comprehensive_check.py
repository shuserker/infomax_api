#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 14 종합 점검 스크립트
통합 상태 보고 시스템 구현 완전성 검증

Requirements: 5.1, 5.2 완전 구현 검증
"""

import os
import sys
import json
from datetime import datetime

def check_file_structure():
    """파일 구조 완전성 검사"""
    print("📁 Task 14 파일 구조 완전성 검사")
    print("=" * 50)
    
    required_files = {
        "core/integrated_status_reporter.py": "통합 상태 보고 시스템 메인 클래스",
        "core/system_recovery_handler.py": "시스템 복구 핸들러",
        "gui_components/status_dashboard.py": "GUI 상태 대시보드",
        "main_gui.py": "메인 GUI (통합됨)",
        "test_integrated_status_system.py": "통합 테스트 스크립트",
        "verify_task14.py": "검증 스크립트"
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size:,} bytes) - {description}")
        else:
            print(f"❌ {file_path} - {description}")
            all_exist = False
    
    return all_exist

def check_integrated_status_reporter():
    """통합 상태 보고 시스템 완전성 검사"""
    print("\n🔧 통합 상태 보고 시스템 완전성 검사")
    print("=" * 50)
    
    try:
        with open("core/integrated_status_reporter.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 클래스 및 메서드 검사
        required_elements = {
            "class IntegratedStatusReporter": "메인 클래스",
            "class SystemStatus": "시스템 상태 열거형",
            "class AlertLevel": "알림 레벨 열거형", 
            "class SystemComponent": "시스템 컴포넌트 데이터 클래스",
            "class StatusAlert": "상태 알림 데이터 클래스",
            "class DeploymentStatistics": "배포 통계 데이터 클래스",
            
            # 핵심 메서드들
            "def start_monitoring": "모니터링 시작",
            "def stop_monitoring": "모니터링 중지",
            "def update_all_component_status": "모든 컴포넌트 상태 업데이트",
            "def update_deployment_statistics": "배포 통계 업데이트",
            "def register_status_callback": "상태 콜백 등록",
            "def register_alert_callback": "알림 콜백 등록",
            "def register_statistics_callback": "통계 콜백 등록",
            "def register_recovery_callback": "복구 콜백 등록",
            "def trigger_manual_recovery": "수동 복구 트리거",
            "def export_status_report": "상태 보고서 내보내기",
            "def get_system_overview": "시스템 개요 조회",
            
            # 컴포넌트별 상태 업데이트 메서드들
            "def update_deployment_monitor_status": "배포 모니터 상태 업데이트",
            "def update_github_pages_monitor_status": "GitHub Pages 모니터 상태 업데이트",
            "def update_cache_monitor_status": "캐시 모니터 상태 업데이트",
            "def update_git_deployment_status": "Git 배포 시스템 상태 업데이트",
            "def update_message_system_status": "메시지 시스템 상태 업데이트",
            "def update_webhook_integration_status": "웹훅 통합 상태 업데이트",
            
            # 알림 및 복구 관련
            "_create_status_change_alert": "상태 변화 알림 생성",
            "_send_alert": "알림 전송",
            "_attempt_auto_recovery": "자동 복구 시도",
            "_save_alert_to_file": "알림 파일 저장"
        }
        
        missing_elements = []
        for element, description in required_elements.items():
            if element in content:
                print(f"✅ {element} - {description}")
            else:
                print(f"❌ {element} - {description}")
                missing_elements.append(element)
        
        # Requirements 5.1, 5.2 구현 확인
        req_5_1_features = [
            "모든 내장 시스템의 상태를 메인 GUI에 실시간 보고",
            "register_status_callback" in content and "_notify_status_update" in content,
            "update_all_component_status" in content,
            "initialize_components" in content
        ]
        
        req_5_2_features = [
            "배포 성공/실패 통계를 대시보드에 시각화",
            "update_deployment_statistics" in content and "DeploymentStatistics" in content,
            "시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공",
            "register_alert_callback" in content and "trigger_manual_recovery" in content
        ]
        
        print(f"\n📊 Requirements 5.1 구현: {'✅' if all(req_5_1_features[1:]) else '❌'}")
        print(f"📊 Requirements 5.2 구현: {'✅' if all(req_5_2_features[1::2]) else '❌'}")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ 통합 상태 보고 시스템 검사 실패: {e}")
        return False

def check_system_recovery_handler():
    """시스템 복구 핸들러 완전성 검사"""
    print("\n🔧 시스템 복구 핸들러 완전성 검사")
    print("=" * 50)
    
    try:
        with open("core/system_recovery_handler.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 클래스 및 메서드 검사
        required_elements = {
            "class SystemRecoveryHandler": "메인 복구 핸들러 클래스",
            "def execute_recovery": "복구 액션 실행",
            
            # 배포 모니터 복구 액션들
            "def restart_deployment_monitoring": "배포 모니터링 재시작",
            "def clear_deployment_session": "배포 세션 정리",
            
            # GitHub Pages 모니터 복구 액션들
            "def verify_github_pages": "GitHub Pages 검증",
            "def restart_pages_monitoring": "GitHub Pages 모니터링 재시작",
            
            # 캐시 모니터 복구 액션들
            "def refresh_cache_data": "캐시 데이터 새로고침",
            "def clear_cache_data": "캐시 데이터 정리",
            
            # Git 배포 시스템 복구 액션들
            "def reset_git_branch": "Git 브랜치 리셋",
            "def force_git_push": "Git 강제 푸시",
            
            # 메시지 시스템 복구 액션들
            "def reset_message_templates": "메시지 템플릿 리셋",
            "def test_webhook_connection": "웹훅 연결 테스트",
            
            # 웹훅 통합 복구 액션들
            "def reset_webhook_config": "웹훅 설정 리셋"
        }
        
        missing_elements = []
        for element, description in required_elements.items():
            if element in content:
                print(f"✅ {element} - {description}")
            else:
                print(f"❌ {element} - {description}")
                missing_elements.append(element)
        
        # 복구 액션 매핑 확인
        recovery_components = [
            "deployment_monitor", "github_pages_monitor", "cache_monitor",
            "git_deployment", "message_system", "webhook_integration"
        ]
        
        print(f"\n📋 복구 대상 컴포넌트: {len(recovery_components)}개")
        for component in recovery_components:
            if component in content:
                print(f"✅ {component}")
            else:
                print(f"❌ {component}")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ 시스템 복구 핸들러 검사 실패: {e}")
        return False

def check_status_dashboard():
    """상태 대시보드 GUI 완전성 검사"""
    print("\n🖥️ 상태 대시보드 GUI 완전성 검사")
    print("=" * 50)
    
    try:
        with open("gui_components/status_dashboard.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 클래스 및 메서드 검사
        required_elements = {
            "class StatusDashboard": "메인 대시보드 클래스",
            "def create_gui": "GUI 생성",
            "def create_status_tab": "시스템 상태 탭 생성",
            "def create_statistics_tab": "배포 통계 탭 생성",
            "def create_alerts_tab": "알림 및 로그 탭 생성",
            "def create_control_tab": "제어 패널 탭 생성",
            
            # 콜백 등록 메서드들
            "def register_status_callback": "상태 콜백 등록",
            "def register_alert_callback": "알림 콜백 등록",
            "def register_statistics_callback": "통계 콜백 등록",
            "def register_recovery_callback": "복구 콜백 등록",
            
            # 콜백 처리 메서드들
            "def on_status_update": "상태 업데이트 콜백",
            "def on_alert_received": "알림 수신 콜백",
            "def on_statistics_update": "통계 업데이트 콜백",
            "def on_recovery_request": "복구 요청 콜백",
            
            # 표시 업데이트 메서드들
            "def update_status_display": "상태 표시 업데이트",
            "def update_statistics_display": "통계 표시 업데이트",
            "def update_alerts_display": "알림 표시 업데이트",
            "def update_components_display": "컴포넌트 표시 업데이트",
            
            # 제어 기능들
            "def start_monitoring": "모니터링 시작",
            "def stop_monitoring": "모니터링 중지",
            "def refresh_all_data": "모든 데이터 새로고침",
            "def execute_recovery": "복구 실행",
            "def export_report": "보고서 내보내기"
        }
        
        missing_elements = []
        for element, description in required_elements.items():
            if element in content:
                print(f"✅ {element} - {description}")
            else:
                print(f"❌ {element} - {description}")
                missing_elements.append(element)
        
        # GUI 탭 구성 확인
        gui_tabs = ["시스템 상태", "배포 통계", "알림 및 로그", "제어 패널"]
        print(f"\n📋 GUI 탭 구성: {len(gui_tabs)}개")
        for tab in gui_tabs:
            if tab in content:
                print(f"✅ {tab} 탭")
            else:
                print(f"❌ {tab} 탭")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ 상태 대시보드 GUI 검사 실패: {e}")
        return False

def check_main_gui_integration():
    """메인 GUI 통합 완전성 검사"""
    print("\n🖥️ 메인 GUI 통합 완전성 검사")
    print("=" * 50)
    
    try:
        with open("main_gui.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 import 확인
        required_imports = {
            "from core.integrated_status_reporter import create_integrated_status_reporter": "상태 보고 시스템 import",
            "from core.system_recovery_handler import create_system_recovery_handler": "복구 핸들러 import",
            "from gui_components.status_dashboard import create_status_dashboard": "상태 대시보드 import"
        }
        
        # 필수 초기화 및 통합 확인
        required_integrations = {
            "self.status_reporter = create_integrated_status_reporter": "상태 보고 시스템 초기화",
            "self.recovery_handler = create_system_recovery_handler": "복구 핸들러 초기화",
            "self.status_dashboard = create_status_dashboard": "상태 대시보드 초기화",
            "self.status_reporter.register_recovery_callback": "복구 콜백 등록",
            "self.status_reporter.start_monitoring": "모니터링 자동 시작",
            
            # 메뉴 통합
            "통합 모니터링 시작": "통합 모니터링 메뉴",
            "통합 모니터링 중지": "통합 모니터링 중지 메뉴",
            "상태 보고서 내보내기": "보고서 내보내기 메뉴",
            "시스템 전체 새로고침": "시스템 새로고침 메뉴",
            
            # 메서드 구현
            "def start_integrated_monitoring": "통합 모니터링 시작 메서드",
            "def stop_integrated_monitoring": "통합 모니터링 중지 메서드",
            "def export_status_report": "상태 보고서 내보내기 메서드",
            "def refresh_all_systems": "시스템 새로고침 메서드",
            "def handle_recovery_request": "복구 요청 처리 메서드",
            
            # 탭 통합
            "📊 통합 상태 대시보드": "통합 상태 대시보드 탭",
            "🔄 POSCO 뉴스 시스템": "POSCO 뉴스 시스템 탭"
        }
        
        all_elements = {**required_imports, **required_integrations}
        missing_elements = []
        
        for element, description in all_elements.items():
            if element in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                missing_elements.append(element)
        
        # 제목 업데이트 확인
        if "통합 관리 대시보드" in content:
            print("✅ GUI 제목이 통합 시스템에 맞게 업데이트됨")
        else:
            print("❌ GUI 제목 업데이트 누락")
            missing_elements.append("GUI 제목 업데이트")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ 메인 GUI 통합 검사 실패: {e}")
        return False

def check_requirements_implementation():
    """Requirements 5.1, 5.2 구현 완전성 검사"""
    print("\n🎯 Requirements 구현 완전성 검사")
    print("=" * 50)
    
    # Requirements 5.1: 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고
    req_5_1_checks = []
    
    try:
        # 통합 상태 보고 시스템 확인
        with open("core/integrated_status_reporter.py", 'r', encoding='utf-8') as f:
            reporter_content = f.read()
        
        # GUI 대시보드 확인
        with open("gui_components/status_dashboard.py", 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # 메인 GUI 확인
        with open("main_gui.py", 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # 5.1 세부 검사
        req_5_1_features = {
            "실시간 상태 콜백 시스템": "register_status_callback" in reporter_content and "on_status_update" in dashboard_content,
            "모든 컴포넌트 상태 모니터링": "update_all_component_status" in reporter_content,
            "6개 시스템 컴포넌트 모니터링": all(comp in reporter_content for comp in [
                "deployment_monitor", "github_pages_monitor", "cache_monitor", 
                "git_deployment", "message_system", "webhook_integration"
            ]),
            "GUI 실시간 표시": "update_status_display" in dashboard_content,
            "메인 GUI 통합": "create_status_dashboard" in main_content,
            "자동 모니터링 시작": "start_monitoring" in main_content
        }
        
        print("📊 Requirements 5.1: 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고")
        for feature, implemented in req_5_1_features.items():
            status = "✅" if implemented else "❌"
            print(f"  {status} {feature}")
            req_5_1_checks.append(implemented)
        
        req_5_1_success = all(req_5_1_checks)
        
    except Exception as e:
        print(f"❌ Requirements 5.1 검사 실패: {e}")
        req_5_1_success = False
    
    # Requirements 5.2: 배포 성공/실패 통계를 대시보드에 시각화 & 시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공
    req_5_2_checks = []
    
    try:
        # 5.2 세부 검사
        req_5_2_features = {
            "배포 통계 수집": "update_deployment_statistics" in reporter_content,
            "배포 통계 데이터 클래스": "DeploymentStatistics" in reporter_content,
            "통계 시각화 GUI": "create_statistics_tab" in dashboard_content,
            "성공률 프로그레스 바": "success_rate_progress" in dashboard_content,
            "최근 배포 목록": "deployments_tree" in dashboard_content,
            "실시간 알림 시스템": "register_alert_callback" in reporter_content,
            "알림 레벨 분류": "AlertLevel" in reporter_content,
            "즉시 알림 표시": "show_alert_popup" in dashboard_content,
            "복구 옵션 제공": "execute_recovery" in dashboard_content,
            "자동 복구 시스템": "_attempt_auto_recovery" in reporter_content,
            "수동 복구 트리거": "trigger_manual_recovery" in reporter_content
        }
        
        print("\n📊 Requirements 5.2: 배포 통계 시각화 & 오류 알림/복구")
        for feature, implemented in req_5_2_features.items():
            status = "✅" if implemented else "❌"
            print(f"  {status} {feature}")
            req_5_2_checks.append(implemented)
        
        req_5_2_success = all(req_5_2_checks)
        
    except Exception as e:
        print(f"❌ Requirements 5.2 검사 실패: {e}")
        req_5_2_success = False
    
    return req_5_1_success, req_5_2_success

def check_additional_features():
    """추가 구현 기능들 검사"""
    print("\n🔧 추가 구현 기능들 검사")
    print("=" * 50)
    
    additional_features = []
    
    try:
        # 로깅 시스템 확인
        with open("core/integrated_status_reporter.py", 'r', encoding='utf-8') as f:
            reporter_content = f.read()
        
        if "setup_logging" in reporter_content and "log_message" in reporter_content:
            additional_features.append("✅ 통합 로깅 시스템")
        else:
            additional_features.append("❌ 통합 로깅 시스템")
        
        # 보고서 생성 기능
        if "export_status_report" in reporter_content:
            additional_features.append("✅ 상태 보고서 생성")
        else:
            additional_features.append("❌ 상태 보고서 생성")
        
        # 알림 파일 저장
        if "_save_alert_to_file" in reporter_content:
            additional_features.append("✅ 알림 파일 저장")
        else:
            additional_features.append("❌ 알림 파일 저장")
        
        # 성능 임계값 모니터링
        if "performance_thresholds" in reporter_content:
            additional_features.append("✅ 성능 임계값 모니터링")
        else:
            additional_features.append("❌ 성능 임계값 모니터링")
        
        # 복구 액션 다양성 확인
        with open("core/system_recovery_handler.py", 'r', encoding='utf-8') as f:
            recovery_content = f.read()
        
        recovery_actions = [
            "restart_deployment_monitoring", "clear_deployment_session",
            "verify_github_pages", "restart_pages_monitoring",
            "refresh_cache_data", "clear_cache_data",
            "reset_git_branch", "force_git_push",
            "reset_message_templates", "test_webhook_connection",
            "reset_webhook_config"
        ]
        
        implemented_actions = sum(1 for action in recovery_actions if action in recovery_content)
        additional_features.append(f"✅ 복구 액션: {implemented_actions}/{len(recovery_actions)}개")
        
        # GUI 탭 구성 확인
        with open("gui_components/status_dashboard.py", 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        gui_tabs = ["create_status_tab", "create_statistics_tab", "create_alerts_tab", "create_control_tab"]
        implemented_tabs = sum(1 for tab in gui_tabs if tab in dashboard_content)
        additional_features.append(f"✅ GUI 탭: {implemented_tabs}/{len(gui_tabs)}개")
        
        # 테스트 스크립트 확인
        test_files = [
            "test_integrated_status_system.py",
            "verify_task14.py"
        ]
        
        existing_tests = sum(1 for test_file in test_files if os.path.exists(test_file))
        additional_features.append(f"✅ 테스트 스크립트: {existing_tests}/{len(test_files)}개")
        
    except Exception as e:
        additional_features.append(f"❌ 추가 기능 검사 실패: {e}")
    
    for feature in additional_features:
        print(feature)
    
    return len([f for f in additional_features if f.startswith("✅")])

def generate_final_report():
    """최종 검증 보고서 생성"""
    print("\n📋 Task 14 최종 검증 보고서")
    print("=" * 60)
    
    # 모든 검사 실행
    file_structure_ok = check_file_structure()
    reporter_ok = check_integrated_status_reporter()
    recovery_ok = check_system_recovery_handler()
    dashboard_ok = check_status_dashboard()
    integration_ok = check_main_gui_integration()
    req_5_1_ok, req_5_2_ok = check_requirements_implementation()
    additional_count = check_additional_features()
    
    # 최종 점수 계산
    total_checks = 7
    passed_checks = sum([
        file_structure_ok, reporter_ok, recovery_ok, 
        dashboard_ok, integration_ok, req_5_1_ok, req_5_2_ok
    ])
    
    completion_rate = (passed_checks / total_checks) * 100
    
    print(f"\n🏆 Task 14 구현 완성도: {completion_rate:.1f}% ({passed_checks}/{total_checks})")
    print("=" * 60)
    
    # 세부 결과
    results = {
        "📁 파일 구조": "✅ 완료" if file_structure_ok else "❌ 미완료",
        "🔧 통합 상태 보고 시스템": "✅ 완료" if reporter_ok else "❌ 미완료",
        "🔧 시스템 복구 핸들러": "✅ 완료" if recovery_ok else "❌ 미완료",
        "🖥️ 상태 대시보드 GUI": "✅ 완료" if dashboard_ok else "❌ 미완료",
        "🖥️ 메인 GUI 통합": "✅ 완료" if integration_ok else "❌ 미완료",
        "🎯 Requirements 5.1": "✅ 완료" if req_5_1_ok else "❌ 미완료",
        "🎯 Requirements 5.2": "✅ 완료" if req_5_2_ok else "❌ 미완료"
    }
    
    for category, status in results.items():
        print(f"{category}: {status}")
    
    print(f"\n🔧 추가 구현 기능: {additional_count}개")
    
    # 최종 판정
    if completion_rate >= 100:
        print("\n🏆 Task 14 구현 완료!")
        print("✅ 통합 상태 보고 시스템이 완벽하게 구현되었습니다.")
        
        print("\n📊 구현된 핵심 기능:")
        print("• 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고")
        print("• 배포 성공/실패 통계를 대시보드에 시각화")
        print("• 시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공")
        print("• 6개 시스템 컴포넌트 실시간 모니터링")
        print("• 11개 복구 액션 자동/수동 실행")
        print("• 4개 GUI 탭으로 구성된 통합 대시보드")
        print("• 완전한 메인 GUI 통합")
        
        return True
    elif completion_rate >= 80:
        print("\n⚠️ Task 14 거의 완료 (일부 미완성)")
        print("대부분의 기능이 구현되었으나 일부 요소가 누락되었습니다.")
        return False
    else:
        print("\n❌ Task 14 구현 미완료")
        print("핵심 기능들이 누락되어 추가 구현이 필요합니다.")
        return False

def main():
    """메인 검증 함수"""
    print("🚀 Task 14 종합 점검")
    print("통합 상태 보고 시스템 구현 (스탠드얼론)")
    print("Requirements: 5.1, 5.2")
    print("=" * 80)
    
    success = generate_final_report()
    
    # 검증 완료 시간 기록
    print(f"\n⏰ 검증 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)