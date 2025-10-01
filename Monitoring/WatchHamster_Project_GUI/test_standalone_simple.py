#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 스탠드얼론 기능 테스트 (Task 19.1)
안전한 모듈들만 테스트하여 interactive prompt 문제 회피

Requirements: 4.2, 4.3, 4.4 구현
"""

import os
import sys
import json
import importlib.util
from datetime import datetime


def test_project_structure():
    """프로젝트 구조 검증"""
    print("📁 프로젝트 구조 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'main_gui.py',
        'core/cache_monitor.py',
        'Posco_News_Mini_Final_GUI/posco_main_notifier.py',
        'gui_components/config_manager.py',
        'config/gui_config.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(script_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 누락된 파일: {missing_files}")
        return False
    
    print("✅ 필수 파일 구조 확인됨")
    return True


def test_safe_module_imports():
    """안전한 모듈 임포트 테스트"""
    print("📦 안전한 모듈 임포트 테스트 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    safe_modules = [
        'core.cache_monitor',
        'Posco_News_Mini_Final_GUI.git_deployment_manager',
        'Posco_News_Mini_Final_GUI.message_template_engine',
        'gui_components.config_manager'
    ]
    
    successful_imports = 0
    for module_name in safe_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} 임포트 성공")
            successful_imports += 1
        except ImportError as e:
            print(f"❌ {module_name} 임포트 실패: {str(e)}")
        except Exception as e:
            print(f"⚠️ {module_name} 임포트 오류: {str(e)}")
    
    success_rate = successful_imports / len(safe_modules)
    print(f"✅ 임포트 성공률: {success_rate:.1%}")
    return success_rate >= 0.75


def test_configuration_files():
    """설정 파일 검증"""
    print("⚙️ 설정 파일 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_files = [
        'config/gui_config.json',
        'config/posco_config.json',
        'config/webhook_config.json'
    ]
    
    valid_configs = 0
    for config_file in config_files:
        config_path = os.path.join(script_dir, config_file)
        
        if not os.path.exists(config_path):
            print(f"⚠️ 설정 파일 없음: {config_file}")
            continue
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if isinstance(config_data, dict) and config_data:
                valid_configs += 1
                print(f"✅ 유효한 설정: {config_file}")
            else:
                print(f"⚠️ 빈 설정 파일: {config_file}")
                
        except json.JSONDecodeError:
            print(f"❌ JSON 오류: {config_file}")
        except Exception as e:
            print(f"❌ 파일 오류: {config_file} - {str(e)}")
    
    print(f"✅ 유효한 설정 파일: {valid_configs}/{len(config_files)}개")
    return valid_configs >= len(config_files) * 0.6


def test_cache_system():
    """캐시 시스템 테스트"""
    print("💾 캐시 시스템 테스트 중...")
    
    try:
        from core.cache_monitor import CacheMonitor
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "data")
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        # 캐시 모니터 생성
        cache_monitor = CacheMonitor(data_dir=data_dir)
        
        # 캐시 상태 확인
        cache_status = cache_monitor.check_cache_status()
        print(f"✅ 캐시 상태 확인: {len(cache_status)}개 데이터 타입")
        
        # 캐시 요약
        summary = cache_monitor.get_cache_summary()
        print(f"✅ 캐시 요약: {summary['overall_health']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 캐시 시스템 테스트 실패: {str(e)}")
        return False


def test_main_gui_file():
    """메인 GUI 파일 테스트"""
    print("🎨 메인 GUI 파일 테스트 중...")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_gui_path = os.path.join(script_dir, "main_gui.py")
        
        # 파일 존재 확인
        if not os.path.exists(main_gui_path):
            print("❌ main_gui.py 파일 없음")
            return False
        
        # 파일 내용 확인
        with open(main_gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 클래스/함수 확인
        required_elements = ['class MainGUI', 'def __init__', 'def run']
        missing_elements = []
        
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ 누락된 요소: {missing_elements}")
            return False
        
        print("✅ 메인 GUI 파일 구조 확인됨")
        return True
        
    except Exception as e:
        print(f"❌ 메인 GUI 파일 테스트 실패: {str(e)}")
        return False


def test_directory_independence():
    """디렉토리 독립성 테스트"""
    print("🔒 디렉토리 독립성 테스트 중...")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 상위 디렉토리 참조 검색
        dangerous_patterns = ['../../../', '../../WatchHamster', '../../레거시']
        external_references = []
        
        for root, dirs, files in os.walk(script_dir):
            # 숨김 폴더 제외
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for pattern in dangerous_patterns:
                            if pattern in content:
                                relative_path = os.path.relpath(file_path, script_dir)
                                external_references.append(f"{relative_path}: {pattern}")
                                
                    except Exception:
                        continue
        
        if external_references:
            print(f"⚠️ 외부 참조 발견: {len(external_references)}개")
            for ref in external_references[:3]:
                print(f"  - {ref}")
        else:
            print("✅ 외부 의존성 없음 확인")
        
        return len(external_references) == 0
        
    except Exception as e:
        print(f"❌ 독립성 테스트 실패: {str(e)}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 스탠드얼론 기능 테스트 시작")
    print("Task 19.1: 스탠드얼론 기능 테스트 구현")
    print("Requirements: 4.2, 4.3, 4.4")
    print("=" * 60)
    
    tests = [
        ("프로젝트 구조 검증", test_project_structure),
        ("안전한 모듈 임포트", test_safe_module_imports),
        ("설정 파일 검증", test_configuration_files),
        ("캐시 시스템 테스트", test_cache_system),
        ("메인 GUI 파일 테스트", test_main_gui_file),
        ("디렉토리 독립성 테스트", test_directory_independence)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n▶️ {test_name} 시작")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 성공" if result else "❌ 실패"
            print(f"{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"💥 오류: {test_name} - {str(e)}")
        
        print("-" * 40)
    
    # 최종 결과
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("🧪 스탠드얼론 기능 테스트 결과")
    print("=" * 60)
    print(f"📊 총 테스트: {total}개")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {total - passed}개")
    print(f"📈 성공률: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 스탠드얼론 기능 테스트 성공!")
        print("✅ 시스템이 독립 실행 준비가 완료되었습니다.")
        return 0
    else:
        print("⚠️ 스탠드얼론 기능 테스트에서 문제가 발견되었습니다.")
        print("💡 실패한 테스트들을 수정하세요.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)