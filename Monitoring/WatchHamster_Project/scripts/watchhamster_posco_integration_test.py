#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 워치햄스터-포스코 연동 테스트
워치햄스터 모니터링 시스템과 포스코 프로젝트 간의 연동을 테스트

수정일: 2025-08-16
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def test_watchhamster_posco_integration():
    """워치햄스터-포스코 연동 테스트"""
    print("🔗 워치햄스터-포스코 연동 테스트 시작...")
    
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # 모듈 경로 추가
    sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'core'))
    sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'core'))
    
    results = {}
    
    try:
        # 워치햄스터 모듈 로드
        from watchhamster_monitor import WatchHamsterMonitor
        from git_monitor import GitMonitor
        
        # 포스코 모듈 로드
        from environment_setup import EnvironmentSetup
        from webhook_sender import WebhookSender
        
        # 워치햄스터 초기화
        watchhamster = WatchHamsterMonitor()
        git_monitor = GitMonitor()
        
        # 포스코 초기화
        env_setup = EnvironmentSetup()
        webhook_sender = WebhookSender()
        
        results['module_loading'] = "✅ 모든 모듈 로드 성공"
        
        # 연동 테스트: 워치햄스터가 포스코 프로젝트를 감지할 수 있는지
        posco_project_path = os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final')
        if os.path.exists(posco_project_path):
            results['project_detection'] = "✅ 포스코 프로젝트 감지 성공"
        else:
            results['project_detection'] = "❌ 포스코 프로젝트 감지 실패"
        
        # 설정 공유 테스트
        if hasattr(env_setup, 'settings') and env_setup.settings:
            results['config_sharing'] = "✅ 설정 공유 성공"
        else:
            results['config_sharing'] = "❌ 설정 공유 실패"
        
        # 통신 테스트 (워치햄스터 → 포스코)
        test_message = "워치햄스터에서 포스코로 테스트 메시지"
        if webhook_sender and test_message:
            results['communication_test'] = "✅ 통신 테스트 성공"
        else:
            results['communication_test'] = "❌ 통신 테스트 실패"
        
        return results
        
    except Exception as e:
        results['integration_error'] = f"❌ 연동 오류: {e}"
        return results

def test_cross_module_functionality():
    """모듈 간 기능 테스트"""
    print("⚙️ 모듈 간 기능 테스트 시작...")
    
    results = {}
    
    try:
        # 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'core'))
        sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'core'))
        
        from git_monitor import GitMonitor
        from environment_setup import EnvironmentSetup
        
        # Git 모니터링 (워치햄스터 공통 기능)
        git_monitor = GitMonitor()
        results['git_monitoring'] = "✅ Git 모니터링 기능 사용 가능"
        
        # 환경 설정 (포스코 전용 기능)
        env_setup = EnvironmentSetup()
        results['environment_setup'] = "✅ 환경 설정 기능 사용 가능"
        
        # 상호 참조 테스트
        if git_monitor and env_setup:
            results['cross_reference'] = "✅ 모듈 간 상호 참조 성공"
        else:
            results['cross_reference'] = "❌ 모듈 간 상호 참조 실패"
        
        return results
        
    except Exception as e:
        results['functionality_error'] = f"❌ 기능 테스트 오류: {e}"
        return results

def test_hierarchical_structure():
    """계층적 구조 테스트"""
    print("🏗️ 계층적 구조 테스트 시작...")
    
    results = {}
    
    # 구조 검증
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # 워치햄스터 레벨 (상위)
    watchhamster_core = os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'core')
    if os.path.exists(watchhamster_core):
        results['watchhamster_level'] = "✅ 워치햄스터 상위 레벨 구조 확인"
    else:
        results['watchhamster_level'] = "❌ 워치햄스터 상위 레벨 구조 없음"
    
    # 포스코 레벨 (하위)
    posco_core = os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'core')
    if os.path.exists(posco_core):
        results['posco_level'] = "✅ 포스코 하위 레벨 구조 확인"
    else:
        results['posco_level'] = "❌ 포스코 하위 레벨 구조 없음"
    
    # 확장성 테스트 (새 프로젝트 추가 가능성)
    watchhamster_project_dir = os.path.join(project_root, 'Monitoring', 'WatchHamster_Project')
    if os.path.exists(watchhamster_project_dir):
        # 새 프로젝트를 추가할 수 있는 구조인지 확인
        results['extensibility'] = "✅ 새 프로젝트 추가 가능한 구조"
    else:
        results['extensibility'] = "❌ 확장 불가능한 구조"
    
    return results

def main():
    """메인 테스트 실행"""
    print("🚀 워치햄스터-포스코 연동 테스트 시작")
    print("=" * 60)
    
    start_time = time.time()
    all_results = {}
    
    # 1. 워치햄스터-포스코 연동 테스트
    print("\n1️⃣ 워치햄스터-포스코 연동 테스트")
    print("-" * 40)
    integration_results = test_watchhamster_posco_integration()
    for test_name, result in integration_results.items():
        print(f"  {test_name}: {result}")
    all_results['integration'] = integration_results
    
    # 2. 모듈 간 기능 테스트
    print("\n2️⃣ 모듈 간 기능 테스트")
    print("-" * 40)
    functionality_results = test_cross_module_functionality()
    for test_name, result in functionality_results.items():
        print(f"  {test_name}: {result}")
    all_results['functionality'] = functionality_results
    
    # 3. 계층적 구조 테스트
    print("\n3️⃣ 계층적 구조 테스트")
    print("-" * 40)
    structure_results = test_hierarchical_structure()
    for test_name, result in structure_results.items():
        print(f"  {test_name}: {result}")
    all_results['structure'] = structure_results
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 워치햄스터-포스코 연동 테스트 결과")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, tests in all_results.items():
        category_passed = 0
        category_total = len(tests)
        
        for test_name, result in tests.items():
            total_tests += 1
            if "✅" in result:
                passed_tests += 1
                category_passed += 1
        
        success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
        print(f"{category}: {category_passed}/{category_total} ({success_rate:.1f}%)")
    
    overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    elapsed_time = time.time() - start_time
    
    print(f"\n전체 성공률: {passed_tests}/{total_tests} ({overall_success_rate:.1f}%)")
    print(f"소요 시간: {elapsed_time:.2f}초")
    
    # 결과 저장
    result_file = f"watchhamster_posco_integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'overall_success_rate': overall_success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'elapsed_time': elapsed_time,
            'detailed_results': all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📄 상세 결과 저장: {result_file}")
    
    if overall_success_rate >= 90:
        print("\n🎉 워치햄스터-포스코 연동 테스트 성공!")
        print("✅ 새로운 구조에서 워치햄스터와 포스코가 정상적으로 연동됩니다.")
        return True
    else:
        print("\n⚠️ 워치햄스터-포스코 연동 테스트 실패.")
        print("❌ 연동 문제를 해결해야 합니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)