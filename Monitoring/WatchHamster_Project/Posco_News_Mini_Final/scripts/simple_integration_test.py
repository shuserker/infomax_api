#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 POSCO 시스템 간단 통합 테스트
새로운 구조에서 워치햄스터와 포스코 연동 테스트

수정일: 2025-08-16
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def test_module_imports():
    """모듈 import 테스트"""
    print("🔍 모듈 import 테스트 시작...")
    
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    
    # 새로운 구조의 모듈 경로 추가
    sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'core'))
    sys.path.insert(0, os.path.join(project_root, 'Monitoring', 'WatchHamster_Project', 'core'))
    
    results = {}
    
    # 포스코 모듈들 테스트
    try:
        from environment_setup import EnvironmentSetup
        results['environment_setup'] = "✅ 성공"
    except Exception as e:
        results['environment_setup'] = f"❌ 실패: {e}"
    
    try:
        from integrated_api_module import IntegratedAPIModule
        results['integrated_api_module'] = "✅ 성공"
    except Exception as e:
        results['integrated_api_module'] = f"❌ 실패: {e}"
    
    try:
        from news_message_generator import NewsMessageGenerator
        results['news_message_generator'] = "✅ 성공"
    except Exception as e:
        results['news_message_generator'] = f"❌ 실패: {e}"
    
    try:
        from webhook_sender import WebhookSender
        results['webhook_sender'] = "✅ 성공"
    except Exception as e:
        results['webhook_sender'] = f"❌ 실패: {e}"
    
    # 워치햄스터 모듈들 테스트
    try:
        from git_monitor import GitMonitor
        results['git_monitor'] = "✅ 성공"
    except Exception as e:
        results['git_monitor'] = f"❌ 실패: {e}"
    
    try:
        from watchhamster_monitor import WatchHamsterMonitor
        results['watchhamster_monitor'] = "✅ 성공"
    except Exception as e:
        results['watchhamster_monitor'] = f"❌ 실패: {e}"
    
    return results

def test_file_structure():
    """파일 구조 테스트"""
    print("📁 파일 구조 테스트 시작...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    
    required_files = [
        'Monitoring/WatchHamster_Project/core/watchhamster_monitor.py',
        'Monitoring/WatchHamster_Project/core/git_monitor.py',
        'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/environment_setup.py',
        'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/integrated_api_module.py',
        'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/news_message_generator.py',
        'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core/webhook_sender.py',
        'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config/environment_settings.json'
    ]
    
    results = {}
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            results[file_path] = "✅ 존재"
        else:
            results[file_path] = "❌ 없음"
    
    return results

def test_config_loading():
    """설정 파일 로딩 테스트"""
    print("⚙️ 설정 파일 로딩 테스트 시작...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', 'environment_settings.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return {"config_loading": "✅ 성공", "config_keys": list(config.keys())}
    except Exception as e:
        return {"config_loading": f"❌ 실패: {e}"}

def test_basic_functionality():
    """기본 기능 테스트"""
    print("🔧 기본 기능 테스트 시작...")
    
    results = {}
    
    # 환경 설정 테스트
    try:
        from environment_setup import EnvironmentSetup
        env_setup = EnvironmentSetup()
        results['environment_setup_init'] = "✅ 초기화 성공"
    except Exception as e:
        results['environment_setup_init'] = f"❌ 초기화 실패: {e}"
    
    # 웹훅 전송기 테스트
    try:
        from webhook_sender import WebhookSender
        webhook = WebhookSender()
        results['webhook_sender_init'] = "✅ 초기화 성공"
    except Exception as e:
        results['webhook_sender_init'] = f"❌ 초기화 실패: {e}"
    
    return results

def main():
    """메인 테스트 실행"""
    print("🚀 POSCO 시스템 간단 통합 테스트 시작")
    print("=" * 60)
    
    start_time = time.time()
    all_results = {}
    
    # 1. 모듈 import 테스트
    print("\n1️⃣ 모듈 Import 테스트")
    print("-" * 30)
    import_results = test_module_imports()
    for module, result in import_results.items():
        print(f"  {module}: {result}")
    all_results['module_imports'] = import_results
    
    # 2. 파일 구조 테스트
    print("\n2️⃣ 파일 구조 테스트")
    print("-" * 30)
    structure_results = test_file_structure()
    for file_path, result in structure_results.items():
        print(f"  {os.path.basename(file_path)}: {result}")
    all_results['file_structure'] = structure_results
    
    # 3. 설정 파일 로딩 테스트
    print("\n3️⃣ 설정 파일 로딩 테스트")
    print("-" * 30)
    config_results = test_config_loading()
    for key, result in config_results.items():
        print(f"  {key}: {result}")
    all_results['config_loading'] = config_results
    
    # 4. 기본 기능 테스트
    print("\n4️⃣ 기본 기능 테스트")
    print("-" * 30)
    functionality_results = test_basic_functionality()
    for func, result in functionality_results.items():
        print(f"  {func}: {result}")
    all_results['basic_functionality'] = functionality_results
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
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
    result_file = f"simple_integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    if overall_success_rate >= 80:
        print("\n🎉 통합 테스트 성공! 새로운 구조가 정상적으로 작동합니다.")
        return True
    else:
        print("\n⚠️ 통합 테스트 실패. 시스템 점검이 필요합니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)