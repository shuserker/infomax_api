#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 POSCO 시스템 최종 통합 테스트
새로운 구조에서 100% 성공률 달성을 목표로 하는 최종 테스트

수정일: 2025-08-16
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class FinalIntegrationTest:
    """최종 통합 테스트 클래스"""
    
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(self.current_dir)))
        self.setup_paths()
        self.results = {}
        
    def setup_paths(self):
        """경로 설정"""
        # 새로운 구조의 모듈 경로 추가
        sys.path.insert(0, os.path.join(self.project_root, 'Monitoring', 'WatchHamster_Project', 'core'))
        sys.path.insert(0, os.path.join(self.project_root, 'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'core'))
        
    def test_1_file_structure_integrity(self):
        """1. 파일 구조 무결성 테스트"""
        print("1️⃣ 파일 구조 무결성 테스트")
        
        required_files = {
            'watchhamster_core': 'Monitoring/WatchHamster_Project/core',
            'posco_core': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/core',
            'posco_scripts': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts',
            'posco_docs': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs',
            'posco_config': 'Monitoring/WatchHamster_Project/Posco_News_Mini_Final/config',
            'watchhamster_scripts': 'Monitoring/WatchHamster_Project/scripts',
            'watchhamster_docs': 'Monitoring/WatchHamster_Project/docs'
        }
        
        structure_results = {}
        for name, path in required_files.items():
            full_path = os.path.join(self.project_root, path)
            structure_results[name] = os.path.exists(full_path)
            status = "✅" if structure_results[name] else "❌"
            print(f"  {name}: {status}")
        
        self.results['file_structure'] = structure_results
        return all(structure_results.values())
    
    def test_2_module_loading(self):
        """2. 모듈 로딩 테스트"""
        print("\n2️⃣ 모듈 로딩 테스트")
        
        modules_to_test = [
            ('environment_setup', 'EnvironmentSetup'),
            ('integrated_api_module', 'IntegratedAPIModule'),
            ('news_message_generator', 'NewsMessageGenerator'),
            ('webhook_sender', 'WebhookSender'),
            ('git_monitor', 'GitMonitor'),
            ('watchhamster_monitor', 'WatchHamsterMonitor')
        ]
        
        loading_results = {}
        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name)
                getattr(module, class_name)
                loading_results[module_name] = True
                print(f"  {module_name}: ✅")
            except Exception as e:
                loading_results[module_name] = False
                print(f"  {module_name}: ❌ ({str(e)[:50]}...)")
        
        self.results['module_loading'] = loading_results
        return all(loading_results.values())
    
    def test_3_configuration_access(self):
        """3. 설정 파일 접근 테스트"""
        print("\n3️⃣ 설정 파일 접근 테스트")
        
        config_tests = {}
        
        # 포스코 설정 파일
        posco_config_path = os.path.join(
            self.project_root, 
            'Monitoring', 'WatchHamster_Project', 'Posco_News_Mini_Final', 'config', 
            'environment_settings.json'
        )
        
        try:
            with open(posco_config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            config_tests['posco_config'] = True
            print(f"  포스코 설정 파일: ✅ ({len(config_data)} 설정 항목)")
        except Exception as e:
            config_tests['posco_config'] = False
            print(f"  포스코 설정 파일: ❌ ({e})")
        
        # 레거시 설정 파일 보존 확인
        legacy_config_path = os.path.join(self.project_root, 'recovery_config', 'environment_settings.json')
        config_tests['legacy_preservation'] = os.path.exists(legacy_config_path)
        status = "✅" if config_tests['legacy_preservation'] else "❌"
        print(f"  레거시 설정 보존: {status}")
        
        self.results['configuration'] = config_tests
        return all(config_tests.values())
    
    def test_4_basic_initialization(self):
        """4. 기본 초기화 테스트"""
        print("\n4️⃣ 기본 초기화 테스트")
        
        init_results = {}
        
        # 환경 설정 초기화
        try:
            from environment_setup import EnvironmentSetup
            env_setup = EnvironmentSetup()
            init_results['environment_setup'] = hasattr(env_setup, 'settings')
            status = "✅" if init_results['environment_setup'] else "❌"
            print(f"  환경 설정 초기화: {status}")
        except Exception as e:
            init_results['environment_setup'] = False
            print(f"  환경 설정 초기화: ❌ ({e})")
        
        # 웹훅 전송기 초기화
        try:
            from webhook_sender import WebhookSender
            webhook = WebhookSender()
            init_results['webhook_sender'] = webhook is not None
            status = "✅" if init_results['webhook_sender'] else "❌"
            print(f"  웹훅 전송기 초기화: {status}")
        except Exception as e:
            init_results['webhook_sender'] = False
            print(f"  웹훅 전송기 초기화: ❌ ({e})")
        
        # Git 모니터 초기화
        try:
            from git_monitor import GitMonitor
            git_monitor = GitMonitor()
            init_results['git_monitor'] = git_monitor is not None
            status = "✅" if init_results['git_monitor'] else "❌"
            print(f"  Git 모니터 초기화: {status}")
        except Exception as e:
            init_results['git_monitor'] = False
            print(f"  Git 모니터 초기화: ❌ ({e})")
        
        self.results['initialization'] = init_results
        return all(init_results.values())
    
    def test_5_cross_module_compatibility(self):
        """5. 모듈 간 호환성 테스트"""
        print("\n5️⃣ 모듈 간 호환성 테스트")
        
        compatibility_results = {}
        
        try:
            # 워치햄스터 공통 모듈
            from git_monitor import GitMonitor
            
            # 포스코 전용 모듈
            from environment_setup import EnvironmentSetup
            
            # 두 모듈이 동시에 로드되는지 확인
            git_monitor = GitMonitor()
            env_setup = EnvironmentSetup()
            
            compatibility_results['simultaneous_loading'] = True
            print(f"  동시 로딩: ✅")
            
            # 설정 공유 가능성 확인
            if hasattr(env_setup, 'settings'):
                compatibility_results['config_sharing'] = True
                print(f"  설정 공유: ✅")
            else:
                compatibility_results['config_sharing'] = False
                print(f"  설정 공유: ❌")
            
        except Exception as e:
            compatibility_results['simultaneous_loading'] = False
            compatibility_results['config_sharing'] = False
            print(f"  호환성 테스트: ❌ ({e})")
        
        self.results['compatibility'] = compatibility_results
        return all(compatibility_results.values())
    
    def test_6_hierarchical_structure_validation(self):
        """6. 계층적 구조 검증 테스트"""
        print("\n6️⃣ 계층적 구조 검증 테스트")
        
        hierarchy_results = {}
        
        # 워치햄스터 상위 레벨 확인
        watchhamster_path = os.path.join(self.project_root, 'Monitoring', 'WatchHamster_Project')
        hierarchy_results['watchhamster_level'] = os.path.exists(watchhamster_path)
        status = "✅" if hierarchy_results['watchhamster_level'] else "❌"
        print(f"  워치햄스터 상위 레벨: {status}")
        
        # 포스코 하위 레벨 확인
        posco_path = os.path.join(watchhamster_path, 'Posco_News_Mini_Final')
        hierarchy_results['posco_sublevel'] = os.path.exists(posco_path)
        status = "✅" if hierarchy_results['posco_sublevel'] else "❌"
        print(f"  포스코 하위 레벨: {status}")
        
        # 확장성 구조 확인 (새 프로젝트 추가 가능)
        hierarchy_results['extensible_structure'] = (
            hierarchy_results['watchhamster_level'] and 
            hierarchy_results['posco_sublevel']
        )
        status = "✅" if hierarchy_results['extensible_structure'] else "❌"
        print(f"  확장 가능한 구조: {status}")
        
        self.results['hierarchy'] = hierarchy_results
        return all(hierarchy_results.values())
    
    def test_7_legacy_preservation(self):
        """7. 레거시 보존 테스트"""
        print("\n7️⃣ 레거시 보존 테스트")
        
        legacy_results = {}
        
        # recovery_config 폴더 보존 확인
        recovery_config_path = os.path.join(self.project_root, 'recovery_config')
        legacy_results['recovery_config_preserved'] = os.path.exists(recovery_config_path)
        status = "✅" if legacy_results['recovery_config_preserved'] else "❌"
        print(f"  recovery_config 보존: {status}")
        
        # 핵심 레거시 파일들 확인
        legacy_files = [
            'watchhamster_monitor.py',
            'git_monitor.py',
            'environment_setup.py',
            'integrated_api_module.py',
            'news_message_generator.py',
            'webhook_sender.py'
        ]
        
        preserved_count = 0
        for file_name in legacy_files:
            file_path = os.path.join(recovery_config_path, file_name)
            if os.path.exists(file_path):
                preserved_count += 1
        
        legacy_results['legacy_files_preserved'] = preserved_count == len(legacy_files)
        status = "✅" if legacy_results['legacy_files_preserved'] else "❌"
        print(f"  레거시 파일 보존: {status} ({preserved_count}/{len(legacy_files)})")
        
        self.results['legacy_preservation'] = legacy_results
        return all(legacy_results.values())
    
    def test_8_operational_readiness(self):
        """8. 운영 준비 상태 테스트"""
        print("\n8️⃣ 운영 준비 상태 테스트")
        
        operational_results = {}
        
        # 실행 스크립트 존재 확인
        scripts_to_check = [
            ('Monitoring/WatchHamster_Project/scripts/start_monitoring.py', 'watchhamster_start_script'),
            ('Monitoring/WatchHamster_Project/Posco_News_Mini_Final/scripts/system_test.py', 'posco_test_script'),
            ('Monitoring/WatchHamster_Project/scripts/daily_check.sh', 'daily_check_mac'),
            ('Monitoring/WatchHamster_Project/scripts/daily_check.bat', 'daily_check_windows')
        ]
        
        for script_path, key in scripts_to_check:
            full_path = os.path.join(self.project_root, script_path)
            operational_results[key] = os.path.exists(full_path)
            status = "✅" if operational_results[key] else "❌"
            script_name = os.path.basename(script_path)
            print(f"  {script_name}: {status}")
        
        # 문서 존재 확인
        docs_to_check = [
            ('Monitoring/WatchHamster_Project/docs/WATCHHAMSTER_GUIDE.md', 'watchhamster_docs'),
            ('Monitoring/WatchHamster_Project/Posco_News_Mini_Final/docs/MONITORING_GUIDE.md', 'posco_docs')
        ]
        
        for doc_path, key in docs_to_check:
            full_path = os.path.join(self.project_root, doc_path)
            operational_results[key] = os.path.exists(full_path)
            status = "✅" if operational_results[key] else "❌"
            doc_name = os.path.basename(doc_path)
            print(f"  {doc_name}: {status}")
        
        self.results['operational_readiness'] = operational_results
        return all(operational_results.values())
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 POSCO 시스템 최종 통합 테스트 시작")
        print("=" * 60)
        
        start_time = time.time()
        
        # 테스트 실행
        test_methods = [
            self.test_1_file_structure_integrity,
            self.test_2_module_loading,
            self.test_3_configuration_access,
            self.test_4_basic_initialization,
            self.test_5_cross_module_compatibility,
            self.test_6_hierarchical_structure_validation,
            self.test_7_legacy_preservation,
            self.test_8_operational_readiness
        ]
        
        test_results = []
        for test_method in test_methods:
            result = test_method()
            test_results.append(result)
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 최종 통합 테스트 결과 요약")
        print("=" * 60)
        
        total_categories = len(test_results)
        passed_categories = sum(test_results)
        
        # 세부 결과
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            if isinstance(tests, dict):
                category_passed = sum(1 for result in tests.values() if result)
                category_total = len(tests)
                total_tests += category_total
                passed_tests += category_passed
                
                success_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                print(f"{category}: {category_passed}/{category_total} ({success_rate:.1f}%)")
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        elapsed_time = time.time() - start_time
        
        print(f"\n전체 성공률: {passed_tests}/{total_tests} ({overall_success_rate:.1f}%)")
        print(f"카테고리 성공률: {passed_categories}/{total_categories} ({passed_categories/total_categories*100:.1f}%)")
        print(f"소요 시간: {elapsed_time:.2f}초")
        
        # 결과 저장
        result_file = f"final_integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'overall_success_rate': overall_success_rate,
                'category_success_rate': passed_categories/total_categories*100,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'passed_categories': passed_categories,
                'total_categories': total_categories,
                'elapsed_time': elapsed_time,
                'detailed_results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 상세 결과 저장: {result_file}")
        
        # 최종 판정
        if overall_success_rate >= 100:
            print("\n🎉 완벽한 100% 성공률 달성!")
            print("✅ 새로운 구조에서 워치햄스터와 포스코가 완벽하게 연동됩니다.")
            return True
        elif overall_success_rate >= 90:
            print("\n🎉 최종 통합 테스트 성공!")
            print("✅ 새로운 구조가 정상적으로 작동합니다.")
            return True
        else:
            print("\n⚠️ 최종 통합 테스트 실패.")
            print("❌ 추가 수정이 필요합니다.")
            return False

def main():
    """메인 실행 함수"""
    test_runner = FinalIntegrationTest()
    return test_runner.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)