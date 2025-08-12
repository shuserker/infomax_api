#!/usr/bin/env python3
"""
간단한 최종 통합 테스트
Simple Final Integration Test

핵심 기능들이 정상 작동하는지 빠르게 확인합니다.
"""

import system_functionality_verification.py
from pathlib import Path

def test_core_modules():
# REMOVED:     """핵심 모듈 import 테스트"""
# REMOVED:     print("🧪 핵심 모듈 import 테스트")
    
    modules = [
        'naming_convention_manager',
        'file_renaming_system'
    ]
    
    success_count = 0
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: Import 성공")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module}: {str(e)[:50]}...")
    
    return success_count, len(modules)

def test_file_standardization():
    """파일명 표준화 테스트"""
    print("/n📁 파일명 표준화 테스트")
    
    expected_files = [
        "POSCO_News_250808.py",
        "WatchHamster_v3_v3_0_Final_Summary.md",
        "WatchHamster_v3_v3_0_Complete_Guide.md",
        "WatchHamster_v3_v3_0_CrossPlatform_Guide.md"
    ]
    
    success_count = 0
    for filename in expected_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"  ✅ {filename}: 파일 존재")
            success_count += 1
        else:
            print(f"  ❌ {filename}: 파일 없음")
    
    return success_count, len(expected_files)

def test_basic_functionality():
    """기본 기능 테스트"""
    print("/n⚙️ 기본 기능 테스트")
    
    try:
        # naming_convention_manager 기능 테스트
# REMOVED:         from naming_convention_manager.py import get_naming_manager, ComponentType
        manager = get_naming_manager()
        
        # 컴포넌트 감지 테스트
        component = manager.detect_component_type(".naming_backup/config_data_backup/watchhamster.log")
        if component == ComponentType.WATCHHAMSTER:
            print("  ✅ 컴포넌트 감지: 성공")
            test1_success = True
        else:
            print("  ❌ 컴포넌트 감지: 실패")
            test1_success = False
        
        # 파일명 표준화 테스트
        filename = manager.standardize_filename("test.py", ComponentType.WATCHHAMSTER)
        if "WatchHamster_v3.0" in filename:
            print("  ✅ 파일명 표준화: 성공")
            test2_success = True
        else:
            print("  ❌ 파일명 표준화: 실패")
            test2_success = False
        
        return (1 if test1_success else 0) + (1 if test2_success else 0), 2
        
    except Exception as e:
        print(f"  ❌ 기본 기능 테스트 실패: {str(e)[:50]}...")
        return 0, 2

def main():
    """메인 테스트 실행"""
    print("🚀 POSCO 시스템 간단 통합 테스트 시작")
    print("=" * 60)
    
    total_success = 0
    total_tests = 0
    
    # 1. 핵심 모듈 테스트
    success, count = test_core_modules()
    total_success += success
    total_tests += count
    
    # 2. 파일명 표준화 테스트
    success, count = test_file_standardization()
    total_success += success
    total_tests += count
    
    # 3. 기본 기능 테스트
    success, count = test_basic_functionality()
    total_success += success
    total_tests += count
    
    # 결과 요약
    print("/n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"총 테스트: {total_tests}")
    print(f"성공: {total_success}")
    print(f"실패: {total_tests - total_success}")
    print(f"성공률: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("/n🎉 시스템이 정상적으로 작동하고 있습니다!")
        return 0
    else:
        print(f"/n⚠️ 시스템에 문제가 있습니다. 성공률: {success_rate:.1f}%")
        return 1

if __name__ == "__main__":
    sys.exit(main())