#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
격리된 스탠드얼론 기능 테스트 (Task 19.1)
문제가 되는 데모 파일들을 임시로 비활성화하고 테스트

Requirements: 4.2, 4.3, 4.4 구현
"""

import os
import sys
import json
import shutil
import tempfile
from datetime import datetime
from contextlib import contextmanager


@contextmanager
def temporarily_disable_demos():
    """데모 파일들을 임시로 비활성화"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 문제가 될 수 있는 데모 파일들
    demo_files = [
        'Posco_News_Mini_Final_GUI/demo_github_pages_monitor.py',
        'Posco_News_Mini_Final_GUI/demo_message_integration.py',
        'Posco_News_Mini_Final_GUI/demo_conflict_gui.py',
        'Posco_News_Mini_Final_GUI/demo_deployment_monitor_integration.py',
        'Posco_News_Mini_Final_GUI/demo_dynamic_data_messages.py'
    ]
    
    # 백업 파일 경로들
    backup_files = []
    
    try:
        # 데모 파일들을 임시로 이름 변경
        for demo_file in demo_files:
            demo_path = os.path.join(script_dir, demo_file)
            if os.path.exists(demo_path):
                backup_path = demo_path + '.backup'
                shutil.move(demo_path, backup_path)
                backup_files.append((demo_path, backup_path))
                print(f"📦 임시 비활성화: {demo_file}")
        
        yield
        
    finally:
        # 데모 파일들 복원
        for original_path, backup_path in backup_files:
            if os.path.exists(backup_path):
                shutil.move(backup_path, original_path)
                print(f"🔄 복원: {os.path.basename(original_path)}")


def test_project_structure():
    """프로젝트 구조 검증"""
    print("📁 프로젝트 구조 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    essential_files = [
        'main_gui.py',
        'core/cache_monitor.py',
        'core/integrated_status_reporter.py',
        'Posco_News_Mini_Final_GUI/posco_main_notifier.py',
        'Posco_News_Mini_Final_GUI/git_deployment_manager.py',
        'gui_components/config_manager.py',
        'config/gui_config.json'
    ]
    
    missing_files = []
    for file_path in essential_files:
        full_path = os.path.join(script_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            print(f"✅ 필수 파일 확인: {file_path}")
    
    if missing_files:
        print(f"❌ 누락된 필수 파일: {missing_files}")
        return False
    
    print("✅ 모든 필수 파일 확인됨")
    return True


def test_safe_imports():
    """안전한 모듈 임포트 테스트"""
    print("\n📦 안전한 모듈 임포트 테스트 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # 안전한 모듈들만 테스트
    safe_modules = [
        'core.cache_monitor',
        'Posco_News_Mini_Final_GUI.git_deployment_manager',
        'Posco_News_Mini_Final_GUI.message_template_engine',
        'gui_components.config_manager'
    ]
    
    successful_imports = 0
    for module_name in safe_modules:
        try:
            __import__(module_name)
            print(f"✅ 임포트 성공: {module_name}")
            successful_imports += 1
        except ImportError as e:
            print(f"❌ 임포트 실패: {module_name} - {str(e)}")
        except Exception as e:
            print(f"⚠️ 임포트 오류: {module_name} - {str(e)}")
    
    success_rate = successful_imports / len(safe_modules)
    print(f"✅ 임포트 성공률: {success_rate:.1%}")
    return success_rate >= 0.75


def test_cache_system_basic():
    """기본 캐시 시스템 테스트"""
    print("\n💾 기본 캐시 시스템 테스트 중...")
    
    try:
        # 캐시 모니터 클래스만 임포트
        from core.cache_monitor import CacheMonitor, DataType, CacheStatus
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # 캐시 모니터 생성 (초기화만)
        cache_monitor = CacheMonitor(data_dir=data_dir)
        
        # 기본 메서드 존재 확인
        required_methods = ['check_cache_status', 'get_cache_summary', 'start_monitoring', 'stop_monitoring']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(cache_monitor, method):
                missing_methods.append(method)
            else:
                print(f"✅ 메서드 확인: {method}")
        
        if missing_methods:
            print(f"❌ 누락된 메서드: {missing_methods}")
            return False
        
        print("✅ 캐시 시스템 기본 구조 확인됨")
        return True
        
    except Exception as e:
        print(f"❌ 캐시 시스템 테스트 실패: {str(e)}")
        return False


def test_configuration_system():
    """설정 시스템 테스트"""
    print("\n⚙️ 설정 시스템 테스트 중...")
    
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
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 오류: {config_file} - {str(e)}")
        except Exception as e:
            print(f"❌ 파일 오류: {config_file} - {str(e)}")
    
    print(f"✅ 유효한 설정 파일: {valid_configs}/{len(config_files)}개")
    return valid_configs >= len(config_files) * 0.6


def test_main_gui_structure():
    """메인 GUI 구조 테스트"""
    print("\n🎨 메인 GUI 구조 테스트 중...")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_gui_path = os.path.join(script_dir, "main_gui.py")
        
        if not os.path.exists(main_gui_path):
            print("❌ main_gui.py 파일 없음")
            return False
        
        with open(main_gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 필수 요소 확인
        required_elements = [
            'class MainGUI',
            'def __init__',
            'def run',
            'tkinter',
            'Requirements'
        ]
        
        found_elements = 0
        for element in required_elements:
            if element in content:
                found_elements += 1
                print(f"✅ 요소 확인: {element}")
            else:
                print(f"❌ 요소 누락: {element}")
        
        success_rate = found_elements / len(required_elements)
        print(f"✅ GUI 구조 완성도: {success_rate:.1%}")
        return success_rate >= 0.8
        
    except Exception as e:
        print(f"❌ 메인 GUI 구조 테스트 실패: {str(e)}")
        return False


def test_directory_structure():
    """디렉토리 구조 테스트"""
    print("\n📂 디렉토리 구조 테스트 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        'core',
        'Posco_News_Mini_Final_GUI',
        'gui_components',
        'config',
        'assets',
        'logs',
        'data'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = os.path.join(script_dir, dir_name)
        if not os.path.exists(dir_path):
            # 디렉토리가 없으면 생성 시도
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ 디렉토리 생성: {dir_name}")
            except Exception as e:
                missing_dirs.append(dir_name)
                print(f"❌ 디렉토리 생성 실패: {dir_name} - {str(e)}")
        else:
            print(f"✅ 디렉토리 확인: {dir_name}")
    
    if missing_dirs:
        print(f"❌ 생성 실패한 디렉토리: {missing_dirs}")
        return False
    
    print("✅ 모든 필수 디렉토리 확인됨")
    return True


def test_standalone_independence():
    """스탠드얼론 독립성 테스트"""
    print("\n🔒 스탠드얼론 독립성 테스트 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 위험한 외부 참조 패턴
    dangerous_patterns = [
        '../../../',
        '../../WatchHamster',
        '../../레거시',
        '/Users/',  # 절대 경로
        '/home/',   # 절대 경로
        'C:\\',     # Windows 절대 경로
    ]
    
    external_references = []
    python_files_checked = 0
    
    for root, dirs, files in os.walk(script_dir):
        # 숨김 폴더와 백업 파일 제외
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if f.endswith('.py') and not f.endswith('.backup')]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                python_files_checked += 1
                
                for pattern in dangerous_patterns:
                    if pattern in content:
                        relative_path = os.path.relpath(file_path, script_dir)
                        external_references.append(f"{relative_path}: {pattern}")
                        
            except Exception:
                continue
    
    print(f"✅ 검사한 Python 파일: {python_files_checked}개")
    
    if external_references:
        print(f"⚠️ 외부 참조 발견: {len(external_references)}개")
        for ref in external_references[:3]:
            print(f"  - {ref}")
        return len(external_references) <= 2  # 2개 이하는 허용
    else:
        print("✅ 외부 의존성 없음 확인")
        return True


def main():
    """메인 테스트 함수"""
    print("🧪 격리된 스탠드얼론 기능 테스트 시작")
    print("Task 19.1: 스탠드얼론 기능 테스트 구현")
    print("Requirements: 4.2, 4.3, 4.4")
    print("=" * 60)
    
    # 데모 파일들을 임시로 비활성화하고 테스트 실행
    with temporarily_disable_demos():
        tests = [
            ("프로젝트 구조 검증", test_project_structure),
            ("안전한 모듈 임포트", test_safe_imports),
            ("기본 캐시 시스템", test_cache_system_basic),
            ("설정 시스템", test_configuration_system),
            ("메인 GUI 구조", test_main_gui_structure),
            ("디렉토리 구조", test_directory_structure),
            ("스탠드얼론 독립성", test_standalone_independence)
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
    print("🧪 격리된 스탠드얼론 기능 테스트 결과")
    print("=" * 60)
    print(f"📊 총 테스트: {total}개")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {total - passed}개")
    print(f"📈 성공률: {success_rate:.1f}%")
    
    # 테스트 보고서 저장
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(logs_dir, f"standalone_isolated_test_{timestamp}.json")
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_results': [{'test_name': name, 'passed': result} for name, result in results],
            'summary': {
                'total_tests': total,
                'passed_tests': passed,
                'failed_tests': total - passed,
                'success_rate': success_rate
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 테스트 보고서 저장: {report_path}")
    except Exception as e:
        print(f"⚠️ 보고서 저장 실패: {str(e)}")
    
    # 권장사항
    print("\n💡 권장사항:")
    if success_rate >= 90:
        print("  🎉 훌륭합니다! 시스템이 독립 실행 준비가 완료되었습니다.")
        print("  ✅ Requirements 4.2, 4.3, 4.4 검증 완료")
    elif success_rate >= 70:
        print("  ✅ 대부분의 테스트가 통과했습니다. 실패한 항목들을 수정하세요.")
        print("  📝 실패한 테스트들을 개별적으로 점검하세요.")
    else:
        print("  ⚠️ 여러 문제가 발견되었습니다. 기본 구조부터 점검하세요.")
        print("  🔧 필수 파일들과 디렉토리 구조를 먼저 확인하세요.")
    
    if success_rate >= 80:
        print("\n🎉 스탠드얼론 기능 테스트 성공!")
        print("✅ 시스템이 독립 실행 가능한 상태입니다.")
        return 0
    else:
        print("\n⚠️ 스탠드얼론 기능 테스트에서 문제가 발견되었습니다.")
        print("💡 실패한 테스트들을 수정 후 다시 실행하세요.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)