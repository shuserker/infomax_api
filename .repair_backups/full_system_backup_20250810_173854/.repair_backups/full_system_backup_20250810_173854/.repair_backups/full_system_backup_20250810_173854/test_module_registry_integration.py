#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Module Registry Integration
POSCO 시스템 테스트

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import test_config.json
from datetime import datetime

# 현재 스크립트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'Monitoring', 'POSCO News 250808_mini'))

def test_modules_json_exists():
    """modules.json 파일 존재 확인"""
    print("🔍 1. modules.json 파일 존재 확인...")
    
    modules_json_path = os.path.join(current_dir, 'Monitoring', 'POSCO News 250808_mini', '.naming_backup/config_data_backup/Monitoring/Posco_News_mini/modules.json')
    
    if os.path.exists(modules_json_path):
        print(f"✅ modules.json 파일 존재: {modules_json_path}")
        
        # 파일 내용 검증
        try:
with_open(modules_json_path,_'r',_encoding = 'utf-8') as f:
                config = json.load(f)
            
            modules = config.get('modules', {})
            print(f"📋 등록된 모듈 수: {len(modules)}")
            
            for module_name in modules.keys():
                print(f"  • {module_name}")
            
            return True
        except Exception as e:
            print(f"❌ modules.json 파일 파싱 실패: {e}")
            return False
    else:
        print(f"❌ modules.json 파일이 존재하지 않습니다: {modules_json_path}")
        return False

def test_v2_module_registry_import():
# REMOVED:     """v2 ModuleRegistry import 테스트"""
# REMOVED:     print("/n🔍 2. v2 ModuleRegistry import 테스트...")
    
    try:
        # v2 경로 설정
        v2_path = os.path.join(current_dir, 'Monitoring', 'WatchHamster_v3.0')
        if v2_path not in sys.path:
            sys.path.insert(0, v2_path)
        
        # ModuleRegistry import
        from Monitoring/WatchHamster_v3.0/core/module_registry.py import ModuleRegistry_Integration_Summary.md, ModuleStatus
        
# REMOVED:         print("✅ ModuleRegistry import 성공")
        
        # 기본 기능 테스트
        modules_json_path = os.path.join(current_dir, 'Monitoring', 'POSCO News 250808_mini', '.naming_backup/config_data_backup/Monitoring/Posco_News_mini/modules.json')
        registry = ModuleRegistry(modules_json_path)
        
        print("✅ ModuleRegistry 초기화 성공")
        
        # 모듈 목록 조회
        modules = registry.list_modules()
        print(f"📋 로드된 모듈 수: {len(modules)}")
        
        # 시작 순서 조회
        startup_order = registry.get_startup_order()
        print(f"🚀 자동 시작 모듈 수: {len(startup_order)}")
        print(f"🔄 시작 순서: {' → '.join(startup_order)}")
        
        return True
        
    except ImportError as e:
# REMOVED:         print(f"❌ ModuleRegistry import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ ModuleRegistry 테스트 실패: {e}")
        return False

def test_watchhamster_v3_0_integration():
    """WatchHamster v3.0.0 통합 테스트"""
    print("/n🔍 3. WatchHamster v3.0.0 통합 테스트...")
    
    try:
        # 워치햄스터 import
from .comprehensive_repair_backup/monitor_.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log_v3.0.py.backup_20250809_181656 import .naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log v3.00Monitor
        
# REMOVED:         print("✅ PoscoMonitorWatchHamster import 성공")
        
        # WatchHamster v3.0 초기화 (실제 실행하지 않고 초기화만)
        print("🔧 WatchHamster v3.0 초기화 중...")
        watchhamster = WatchHamster v3.00Monitor()
        
        print("✅ WatchHamster v3.0 초기화 성공")
        
        # v2 통합 상태 확인
        v2_status = watchhamster.get_v2_integration_status()
        
        print(f"🎯 v2 아키텍처 활성화: {v2_status.get('v3_0_enabled', False)}")
        
        if v2_status.get('v3_0_enabled'):
            print("🎉 v2 아키텍처 활성화됨!")
            
            # 컴포넌트 상태 확인
            components = v2_status.get('components', {})
            for component, status in components.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {component}: {'활성화' if status else '비활성화'}")
            
            # 관리 대상 프로세스 확인
            managed_processes = v2_status.get('managed_processes', [])
            print(f"📋 관리 대상 프로세스: {len(managed_processes)}개")
            for process in managed_processes:
                print(f"  • {process}")
            
            # 모듈 상태 요약 확인
            if hasattr(watchhamster, 'get_module_status_summary'):
                module_summary = watchhamster.get_module_status_summary()
                if 'error' not in module_summary:
                    print(f"📊 모듈 상태 추적: {module_summary.get('total_modules', 0)}개 모듈")
                    status_counts = module_summary.get('status_counts', {})
                    for status, count in status_counts.items():
                        if count > 0:
                            print(f"  • {status}: {count}개")
        else:
            print("⚠️ v2 아키텍처 비활성화됨")
            fallback_reason = v2_status.get('fallback_reason')
            if fallback_reason:
                print(f"📋 폴백 사유: {fallback_reason}")
        
        return True
        
    except ImportError as e:
        print(f"❌ WatchHamster v3.0 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ WatchHamster v3.0.0 통합 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def test_module_control_functions():
    """모듈 제어 기능 테스트"""
    print("/n🔍 4. 모듈 제어 기능 테스트...")
    
    try:
        from .comprehensive_repair_backup/monitor_.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log_v3.0.py.backup_20250809_181656 import .naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log v3.00Monitor
        
        watchhamster = WatchHamster v3.00Monitor()
        
        if not watchhamster.v3_0_enabled:
            print("⚠️ v2 아키텍처가 비활성화되어 모듈 제어 테스트를 건너뜁니다")
            return True
        
        # 모듈 상태 조회 테스트
        test_module = "posco_main_notifier"
        print(f"🔍 {test_module} 상태 조회 테스트...")
        
        status_result = watchhamster.control_module(test_module, 'status')
        
        if status_result.get('success'):
            print(f"✅ 모듈 상태 조회 성공")
            status_info = status_result.get('status', {})
            if isinstance(status_info, dict):
                process_status = status_info.get('process_status', 'unknown')
                print(f"  📊 프로세스 상태: {process_status}")
        else:
            print(f"⚠️ 모듈 상태 조회 실패: {status_result.get('error', 'Unknown error')}")
        
        # 모듈 상태 요약 테스트
        print("📊 전체 모듈 상태 요약 테스트...")
        summary = watchhamster.get_module_status_summary()
        
        if 'error' not in summary:
            print("✅ 모듈 상태 요약 조회 성공")
            print(f"  📋 총 모듈: {summary.get('total_modules', 0)}개")
            
            status_counts = summary.get('status_counts', {})
            for status, count in status_counts.items():
                if count > 0:
                    print(f"  • {status}: {count}개")
        else:
            print(f"⚠️ 모듈 상태 요약 실패: {summary.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 모듈 제어 기능 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 POSCO WatchHamster v3.0 시작")
    print("=" * 60)
    
    test_results = []
    
    # 테스트 실행
    test_results.append(("modules.json 존재 확인", test_modules_json_exists()))
    test_results.append(("v2 ModuleRegistry import", test_v2_module_registry_import()))
    test_results.append(("WatchHamster v3.0.0 통합", test_watchhamster_v3_0_integration()))
    test_results.append(("모듈 제어 기능", test_module_control_functions()))
    
    # 결과 요약
print("/n"_+_" = " * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status_icon = "✅" if result else "❌"
        status_text = "통과" if result else "실패"
        print(f"{status_icon} {test_name}: {status_text}")
        
        if result:
passed_tests_+ =  1
    
    print(f"/n🎯 전체 결과: {passed_tests}/{total_tests} 테스트 통과")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트 통과! ModuleRegistry 통합이 성공적으로 완료되었습니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 문제를 확인하고 수정해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)