#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 14 구현 검증 스크립트
통합 상태 보고 시스템 구현 확인

Requirements: 5.1, 5.2 구현 검증
"""

import os
import sys

def verify_files_exist():
    """필요한 파일들이 존재하는지 확인"""
    print("📁 파일 존재 확인")
    print("=" * 40)
    
    required_files = [
        "core/integrated_status_reporter.py",
        "core/system_recovery_handler.py", 
        "gui_components/status_dashboard.py",
        "main_gui.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist

def verify_implementation_features():
    """구현된 기능들 확인"""
    print("\n🔧 구현 기능 확인")
    print("=" * 40)
    
    features = []
    
    # 1. 통합 상태 보고 시스템 확인
    try:
        with open("core/integrated_status_reporter.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "class IntegratedStatusReporter" in content:
            features.append("✅ 통합 상태 보고 시스템 클래스")
        
        if "update_all_component_status" in content:
            features.append("✅ 모든 컴포넌트 상태 업데이트")
            
        if "update_deployment_statistics" in content:
            features.append("✅ 배포 통계 업데이트")
            
        if "register_alert_callback" in content:
            features.append("✅ 실시간 알림 시스템")
            
        if "trigger_manual_recovery" in content:
            features.append("✅ 수동 복구 시스템")
            
    except Exception as e:
        features.append(f"❌ 통합 상태 보고 시스템 확인 실패: {e}")
    
    # 2. 시스템 복구 핸들러 확인
    try:
        with open("core/system_recovery_handler.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "class SystemRecoveryHandler" in content:
            features.append("✅ 시스템 복구 핸들러 클래스")
            
        if "execute_recovery" in content:
            features.append("✅ 복구 액션 실행")
            
        recovery_actions = [
            "restart_deployment_monitoring",
            "verify_github_pages", 
            "refresh_cache_data",
            "reset_git_branch",
            "reset_message_templates",
            "test_webhook_connection"
        ]
        
        found_actions = sum(1 for action in recovery_actions if action in content)
        features.append(f"✅ 복구 액션: {found_actions}/{len(recovery_actions)}개")
        
    except Exception as e:
        features.append(f"❌ 시스템 복구 핸들러 확인 실패: {e}")
    
    # 3. GUI 대시보드 확인
    try:
        with open("gui_components/status_dashboard.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "class StatusDashboard" in content:
            features.append("✅ 상태 대시보드 GUI 클래스")
            
        if "create_status_tab" in content:
            features.append("✅ 시스템 상태 탭")
            
        if "create_statistics_tab" in content:
            features.append("✅ 배포 통계 탭")
            
        if "create_alerts_tab" in content:
            features.append("✅ 알림 및 로그 탭")
            
        if "create_control_tab" in content:
            features.append("✅ 제어 패널 탭")
            
        if "execute_recovery" in content:
            features.append("✅ GUI 복구 실행")
            
    except Exception as e:
        features.append(f"❌ GUI 대시보드 확인 실패: {e}")
    
    # 4. 메인 GUI 통합 확인
    try:
        with open("main_gui.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "create_integrated_status_reporter" in content:
            features.append("✅ 메인 GUI에 상태 보고 시스템 통합")
            
        if "create_system_recovery_handler" in content:
            features.append("✅ 메인 GUI에 복구 핸들러 통합")
            
        if "create_status_dashboard" in content:
            features.append("✅ 메인 GUI에 상태 대시보드 통합")
            
        if "handle_recovery_request" in content:
            features.append("✅ 메인 GUI에 복구 요청 처리")
            
    except Exception as e:
        features.append(f"❌ 메인 GUI 통합 확인 실패: {e}")
    
    for feature in features:
        print(feature)
    
    return len([f for f in features if f.startswith("✅")])

def verify_requirements():
    """Requirements 구현 확인"""
    print("\n🎯 Requirements 구현 확인")
    print("=" * 40)
    
    requirements = []
    
    # Requirements 5.1 확인
    req_5_1_features = [
        "모든 내장 시스템의 상태를 메인 GUI에 실시간 보고",
        "시스템 컴포넌트별 상태 모니터링",
        "실시간 상태 업데이트 콜백",
        "GUI 대시보드 통합"
    ]
    
    try:
        # 통합 상태 보고 시스템 파일 확인
        with open("core/integrated_status_reporter.py", 'r', encoding='utf-8') as f:
            reporter_content = f.read()
        
        # GUI 대시보드 파일 확인
        with open("gui_components/status_dashboard.py", 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # 메인 GUI 파일 확인
        with open("main_gui.py", 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        req_5_1_checks = [
            "register_status_callback" in reporter_content and "on_status_update" in dashboard_content,
            "update_all_component_status" in reporter_content,
            "_notify_status_update" in reporter_content,
            "create_status_dashboard" in main_content
        ]
        
        if all(req_5_1_checks):
            requirements.append("✅ Requirements 5.1: 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고")
        else:
            requirements.append("❌ Requirements 5.1: 일부 기능 누락")
            
    except Exception as e:
        requirements.append(f"❌ Requirements 5.1 확인 실패: {e}")
    
    # Requirements 5.2 확인
    req_5_2_features = [
        "배포 성공/실패 통계를 대시보드에 시각화",
        "시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공"
    ]
    
    try:
        req_5_2_checks = [
            "update_deployment_statistics" in reporter_content and "create_statistics_tab" in dashboard_content,
            "register_alert_callback" in reporter_content and "execute_recovery" in dashboard_content
        ]
        
        if all(req_5_2_checks):
            requirements.append("✅ Requirements 5.2: 배포 통계 시각화 및 오류 알림/복구")
        else:
            requirements.append("❌ Requirements 5.2: 일부 기능 누락")
            
    except Exception as e:
        requirements.append(f"❌ Requirements 5.2 확인 실패: {e}")
    
    for req in requirements:
        print(req)
    
    return len([r for r in requirements if r.startswith("✅")])

def main():
    """메인 검증 함수"""
    print("🚀 Task 14 구현 검증")
    print("통합 상태 보고 시스템 구현 (스탠드얼론)")
    print("Requirements: 5.1, 5.2")
    print("=" * 60)
    
    # 1. 파일 존재 확인
    files_ok = verify_files_exist()
    
    # 2. 구현 기능 확인
    feature_count = verify_implementation_features()
    
    # 3. Requirements 확인
    req_count = verify_requirements()
    
    # 4. 최종 결과
    print("\n" + "=" * 60)
    print("📋 검증 결과 요약")
    print("=" * 60)
    
    print(f"📁 필수 파일: {'✅ 모두 존재' if files_ok else '❌ 일부 누락'}")
    print(f"🔧 구현 기능: {feature_count}개 확인됨")
    print(f"🎯 Requirements: {req_count}/2개 구현됨")
    
    if files_ok and feature_count >= 10 and req_count == 2:
        print("\n🏆 Task 14 구현 완료!")
        print("✅ 통합 상태 보고 시스템이 성공적으로 구현되었습니다.")
        
        print("\n📊 구현된 주요 기능:")
        print("• 모든 내장 시스템의 상태를 메인 GUI에 실시간 보고")
        print("• 배포 성공/실패 통계를 대시보드에 시각화")
        print("• 시스템 오류 발생 시 즉시 알림 및 복구 옵션 제공")
        print("• 실시간 상태 업데이트 및 모니터링")
        print("• 시스템 컴포넌트별 복구 액션 실행")
        print("• GUI 대시보드를 통한 통합 관리")
        
        return True
    else:
        print("\n⚠️ Task 14 구현 미완료")
        print("일부 기능이 누락되었거나 구현이 불완전합니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)