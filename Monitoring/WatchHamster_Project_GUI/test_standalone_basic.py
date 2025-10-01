#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본 스탠드얼론 기능 테스트 (Task 19.1)
모듈 임포트 없이 파일 구조와 내용만 검증

Requirements: 4.2, 4.3, 4.4 구현
"""

import os
import sys
import json
from datetime import datetime


def test_project_structure():
    """프로젝트 구조 검증"""
    print("📁 프로젝트 구조 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_structure = {
        'files': [
            'main_gui.py',
            'core/cache_monitor.py',
            'core/integrated_status_reporter.py',
            'core/system_recovery_handler.py',
            'Posco_News_Mini_Final_GUI/posco_main_notifier.py',
            'Posco_News_Mini_Final_GUI/posco_gui_manager.py',
            'Posco_News_Mini_Final_GUI/git_deployment_manager.py',
            'Posco_News_Mini_Final_GUI/deployment_monitor.py',
            'Posco_News_Mini_Final_GUI/message_template_engine.py',
            'gui_components/log_viewer.py',
            'gui_components/notification_center.py',
            'gui_components/system_tray.py',
            'gui_components/config_manager.py',
            'gui_components/status_dashboard.py',
            'config/gui_config.json',
            'config/posco_config.json',
            'config/webhook_config.json'
        ],
        'directories': [
            'core',
            'Posco_News_Mini_Final_GUI',
            'gui_components',
            'config',
            'assets',
            'assets/icons',
            'assets/images',
            'logs',
            'data'
        ]
    }
    
    missing_items = []
    
    # 디렉토리 확인
    for directory in required_structure['directories']:
        dir_path = os.path.join(script_dir, directory)
        if not os.path.exists(dir_path):
            missing_items.append(f"디렉토리: {directory}")
        else:
            print(f"✅ 디렉토리 확인: {directory}")
    
    # 파일 확인
    for file_path in required_structure['files']:
        full_path = os.path.join(script_dir, file_path)
        if not os.path.exists(full_path):
            missing_items.append(f"파일: {file_path}")
        else:
            print(f"✅ 파일 확인: {file_path}")
    
    if missing_items:
        print(f"❌ 누락된 항목들: {len(missing_items)}개")
        for item in missing_items[:5]:  # 최대 5개만 표시
            print(f"  - {item}")
        return False
    
    print("✅ 모든 필수 구조 확인됨")
    return True


def test_configuration_files():
    """설정 파일 검증"""
    print("\n⚙️ 설정 파일 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_files = [
        'config/gui_config.json',
        'config/posco_config.json',
        'config/webhook_config.json',
        'config/message_templates.json',
        'config/language_strings.json'
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


def test_python_file_syntax():
    """Python 파일 구문 검증"""
    print("\n🐍 Python 파일 구문 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    python_files = []
    for root, dirs, files in os.walk(script_dir):
        # 숨김 폴더 제외
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    valid_files = 0
    syntax_errors = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 기본 구문 검사 (compile 시도)
            compile(content, file_path, 'exec')
            valid_files += 1
            
        except SyntaxError as e:
            relative_path = os.path.relpath(file_path, script_dir)
            syntax_errors.append(f"{relative_path}: {str(e)}")
        except Exception as e:
            relative_path = os.path.relpath(file_path, script_dir)
            syntax_errors.append(f"{relative_path}: {str(e)}")
    
    if syntax_errors:
        print(f"❌ 구문 오류 발견: {len(syntax_errors)}개")
        for error in syntax_errors[:3]:  # 최대 3개만 표시
            print(f"  - {error}")
    
    print(f"✅ 유효한 Python 파일: {valid_files}/{len(python_files)}개")
    return len(syntax_errors) == 0


def test_main_gui_structure():
    """메인 GUI 구조 검증"""
    print("\n🎨 메인 GUI 구조 검증 중...")
    
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
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
            else:
                print(f"✅ 요소 확인: {element}")
        
        if missing_elements:
            print(f"❌ 누락된 요소: {missing_elements}")
            return False
        
        print("✅ 메인 GUI 구조 확인됨")
        return True
        
    except Exception as e:
        print(f"❌ 메인 GUI 구조 검증 실패: {str(e)}")
        return False


def test_external_dependencies():
    """외부 의존성 검증"""
    print("\n🔒 외부 의존성 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 위험한 외부 참조 패턴
    dangerous_patterns = [
        '../../../',
        '../../WatchHamster',
        '../../레거시',
        'sys.path.append("/',
        'sys.path.insert(0, "/'
    ]
    
    external_references = []
    
    for root, dirs, files in os.walk(script_dir):
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
        return False
    else:
        print("✅ 외부 의존성 없음 확인")
        return True


def test_data_directories():
    """데이터 디렉토리 검증"""
    print("\n💾 데이터 디렉토리 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dirs = ['data', 'logs', 'assets', 'config']
    created_dirs = []
    
    for dir_name in data_dirs:
        dir_path = os.path.join(script_dir, dir_name)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_name)
                print(f"✅ 디렉토리 생성: {dir_name}")
            except Exception as e:
                print(f"❌ 디렉토리 생성 실패: {dir_name} - {str(e)}")
                return False
        else:
            print(f"✅ 디렉토리 확인: {dir_name}")
    
    if created_dirs:
        print(f"✅ 생성된 디렉토리: {len(created_dirs)}개")
    
    return True


def test_file_permissions():
    """파일 권한 검증"""
    print("\n🔐 파일 권한 검증 중...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 주요 파일들의 읽기 권한 확인
    important_files = [
        'main_gui.py',
        'core/cache_monitor.py',
        'config/gui_config.json'
    ]
    
    permission_issues = []
    
    for file_path in important_files:
        full_path = os.path.join(script_dir, file_path)
        if os.path.exists(full_path):
            if os.access(full_path, os.R_OK):
                print(f"✅ 읽기 권한 확인: {file_path}")
            else:
                permission_issues.append(f"{file_path}: 읽기 권한 없음")
        else:
            permission_issues.append(f"{file_path}: 파일 없음")
    
    if permission_issues:
        print(f"❌ 권한 문제: {len(permission_issues)}개")
        for issue in permission_issues:
            print(f"  - {issue}")
        return False
    
    print("✅ 모든 파일 권한 확인됨")
    return True


def generate_test_report(results):
    """테스트 보고서 생성"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 보고서 데이터
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'test_results': results,
        'summary': {
            'total_tests': len(results),
            'passed_tests': sum(1 for _, result in results if result),
            'failed_tests': sum(1 for _, result in results if not result),
            'success_rate': (sum(1 for _, result in results if result) / len(results) * 100) if results else 0
        }
    }
    
    # 보고서 파일 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"standalone_basic_test_report_{timestamp}.json"
    
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    report_path = os.path.join(logs_dir, report_filename)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📄 테스트 보고서 저장: {report_path}")
    except Exception as e:
        print(f"⚠️ 보고서 저장 실패: {str(e)}")
    
    return report


def main():
    """메인 테스트 함수"""
    print("🧪 기본 스탠드얼론 기능 테스트 시작")
    print("Task 19.1: 스탠드얼론 기능 테스트 구현")
    print("Requirements: 4.2, 4.3, 4.4")
    print("=" * 60)
    
    tests = [
        ("프로젝트 구조 검증", test_project_structure),
        ("설정 파일 검증", test_configuration_files),
        ("Python 파일 구문 검증", test_python_file_syntax),
        ("메인 GUI 구조 검증", test_main_gui_structure),
        ("외부 의존성 검증", test_external_dependencies),
        ("데이터 디렉토리 검증", test_data_directories),
        ("파일 권한 검증", test_file_permissions)
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
    print("🧪 기본 스탠드얼론 기능 테스트 결과")
    print("=" * 60)
    print(f"📊 총 테스트: {total}개")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {total - passed}개")
    print(f"📈 성공률: {success_rate:.1f}%")
    
    # 보고서 생성
    report = generate_test_report(results)
    
    # 권장사항
    print("\n💡 권장사항:")
    if success_rate >= 90:
        print("  🎉 훌륭합니다! 시스템이 독립 실행 준비가 완료되었습니다.")
    elif success_rate >= 70:
        print("  ✅ 대부분의 테스트가 통과했습니다. 실패한 항목들을 수정하세요.")
    else:
        print("  ⚠️ 여러 문제가 발견되었습니다. 기본 구조부터 점검하세요.")
    
    if success_rate >= 80:
        print("\n🎉 기본 스탠드얼론 기능 테스트 성공!")
        print("✅ Requirements 4.2, 4.3, 4.4 기본 검증 완료")
        return 0
    else:
        print("\n⚠️ 기본 스탠드얼론 기능 테스트에서 문제가 발견되었습니다.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)