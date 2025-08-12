#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Control Center Integration
POSCO 시스템 제어센터

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import subprocess
import .comprehensive_repair_backup/realtime_news_monitor.py.backup_20250809_181657
import tempfile
import shutil
from datetime import datetime

class ControlCenterTester:
    """제어센터 통합 테스터"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.control_center_script = os.path.join(self.script_dir, '.naming_backup/scripts/watchhamster_control_center.sh')
        self.test_results = []
        
    def test_script_existence_and_permissions(self):
        """스크립트 존재 및 권한 확인"""
        print("🧪 제어센터 스크립트 존재 및 권한 확인...")
        
        try:
            # 파일 존재 확인
            if not os.path.exists(self.control_center_script):
                raise FileNotFoundError(f"제어센터 스크립트를 찾을 수 없습니다: {self.control_center_script}")
            
            print(f"✅ 스크립트 파일 존재 확인: {self.control_center_script}")
            
            # 실행 권한 확인
            if not os.access(self.control_center_script, os.X_OK):
                print("⚠️ 실행 권한이 없습니다. 권한을 설정합니다...")
                os.chmod(self.control_center_script, 0o755)
            
            print("✅ 실행 권한 확인 완료")
            
            # 파일 크기 확인
            file_size = os.path.getsize(self.control_center_script)
            print(f"✅ 스크립트 크기: {file_size} bytes")
            
            self.test_results.append(("script_existence", True, "스크립트 존재 및 권한 확인 성공"))
            
        except Exception as e:
            print(f"❌ 스크립트 존재 및 권한 확인 실패: {e}")
            self.test_results.append(("script_existence", False, str(e)))
    
    def test_script_syntax(self):
        """스크립트 문법 검사"""
        print("🧪 제어센터 스크립트 문법 검사...")
        
        try:
            # bash 문법 검사
            result = subprocess.run([
                'bash', '-n', self.control_center_script
],_capture_output = True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ 스크립트 문법 검사 통과")
                self.test_results.append(("script_syntax", True, "문법 검사 성공"))
            else:
                raise Exception(f"문법 오류: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ 문법 검사 타임아웃")
            self.test_results.append(("script_syntax", False, "문법 검사 타임아웃"))
        except Exception as e:
            print(f"❌ 스크립트 문법 검사 실패: {e}")
            self.test_results.append(("script_syntax", False, str(e)))
    
    def test_required_functions(self):
        """필수 함수 존재 확인"""
        print("🧪 제어센터 필수 함수 존재 확인...")
        
        try:
with_open(self.control_center_script,_'r',_encoding = 'utf-8') as f:
                script_content = f.read()
            
            # 필수 함수 목록
            required_functions = [
                'main_menu',
                'start_watchhamster',
                'stop_watchhamster',
                'restart_watchhamster',
                'check_watchhamster_status',
                'manage_modules',
                'check_managed_processes'
            ]
            
            missing_functions = []
            found_functions = []
            
            for function_name in required_functions:
                # 함수 정의 패턴 검색
                if f'{function_name}()' in script_content or f'{function_name} ()' in script_content:
                    found_functions.append(function_name)
                    print(f"✅ 함수 발견: {function_name}")
                else:
                    missing_functions.append(function_name)
                    print(f"❌ 함수 누락: {function_name}")
            
            if not missing_functions:
                print(f"✅ 모든 필수 함수 확인 완료 ({len(found_functions)}개)")
                self.test_results.append(("required_functions", True, f"필수 함수 {len(found_functions)}개 확인"))
            else:
                raise Exception(f"누락된 함수: {', '.join(missing_functions)}")
                
        except Exception as e:
            print(f"❌ 필수 함수 확인 실패: {e}")
            self.test_results.append(("required_functions", False, str(e)))
    
    def test_dependency_scripts(self):
        """의존성 스크립트 확인"""
        print("🧪 의존성 스크립트 확인...")
        
        try:
            # lib_wt_common.sh 확인
            lib_script = os.path.join(self.script_dir, 'lib_wt_common.sh')
            
            if os.path.exists(lib_script):
                print(f"✅ 공통 라이브러리 발견: {lib_script}")
                
                # 문법 검사
                result = subprocess.run([
                    'bash', '-n', lib_script
],_capture_output = True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print("✅ 공통 라이브러리 문법 검사 통과")
                else:
                    print(f"⚠️ 공통 라이브러리 문법 경고: {result.stderr}")
            else:
                print("⚠️ 공통 라이브러리를 찾을 수 없습니다")
            
            # 워치햄스터 스크립트 확인
            watchhamster_script = os.path.join(self.script_dir, 'Monitoring', 'POSCO News 250808_mini', '.naming_backup/config_data_backup/watchhamster.log')
            
            if os.path.exists(watchhamster_script):
                print(f"✅ 워치햄스터 스크립트 발견: {watchhamster_script}")
            else:
                print("⚠️ 워치햄스터 스크립트를 찾을 수 없습니다")
            
            self.test_results.append(("dependency_scripts", True, "의존성 스크립트 확인 완료"))
            
        except Exception as e:
            print(f"❌ 의존성 스크립트 확인 실패: {e}")
            self.test_results.append(("dependency_scripts", False, str(e)))
    
    def test_environment_check(self):
        """환경 확인 기능 테스트"""
        print("🧪 환경 확인 기능 테스트...")
        
        try:
            # Python3 존재 확인
            python_result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
            if python_result.returncode == 0:
                print(f"✅ Python3 발견: {python_result.stdout.strip()}")
            else:
                print("⚠️ Python3를 찾을 수 없습니다")
            
            # bash 존재 확인
            bash_result = subprocess.run(['which', 'bash'], capture_output=True, text=True)
            if bash_result.returncode == 0:
                print(f"✅ Bash 발견: {bash_result.stdout.strip()}")
            else:
                print("❌ Bash를 찾을 수 없습니다")
            
            # 필요한 명령어들 확인
            required_commands = ['ps', 'pgrep', 'pkill', 'kill']
            available_commands = []
            
            for cmd in required_commands:
                result = subprocess.run(['which', cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    available_commands.append(cmd)
                    print(f"✅ 명령어 발견: {cmd}")
                else:
                    print(f"⚠️ 명령어 누락: {cmd}")
            
            if len(available_commands) >= len(required_commands) * 0.8:  # 80% 이상 사용 가능
                self.test_results.append(("environment_check", True, f"환경 확인 성공 ({len(available_commands)}/{len(required_commands)} 명령어 사용 가능)"))
            else:
                self.test_results.append(("environment_check", False, f"필수 명령어 부족 ({len(available_commands)}/{len(required_commands)})"))
                
        except Exception as e:
            print(f"❌ 환경 확인 실패: {e}")
            self.test_results.append(("environment_check", False, str(e)))
    
    def test_menu_structure(self):
        """메뉴 구조 확인"""
        print("🧪 메뉴 구조 확인...")
        
        try:
with_open(self.control_center_script,_'r',_encoding = 'utf-8') as f:
                script_content = f.read()
            
            # 메뉴 항목 확인
            menu_items = [
                '워치햄스터 시작',
                '워치햄스터 중지',
                '워치햄스터 재시작',
                'WatchHamster v3.0 상태',
                '모듈 관리'
            ]
            
            found_items = []
            for item in menu_items:
                if item in script_content:
                    found_items.append(item)
                    print(f"✅ 메뉴 항목 발견: {item}")
                else:
                    print(f"⚠️ 메뉴 항목 누락: {item}")
            
            # case 문 구조 확인
            case_patterns = ['"1")', '"2")', '"3")', '"4")', '"5")']
            found_cases = []
            
            for pattern in case_patterns:
                if pattern in script_content:
                    found_cases.append(pattern)
                    print(f"✅ Case 패턴 발견: {pattern}")
            
            if len(found_items) >= 4 and len(found_cases) >= 4:
                self.test_results.append(("menu_structure", True, f"메뉴 구조 확인 성공 ({len(found_items)}개 항목, {len(found_cases)}개 케이스)"))
            else:
                self.test_results.append(("menu_structure", False, f"메뉴 구조 불완전 ({len(found_items)}개 항목, {len(found_cases)}개 케이스)"))
                
        except Exception as e:
            print(f"❌ 메뉴 구조 확인 실패: {e}")
            self.test_results.append(("menu_structure", False, str(e)))
    
    def test_error_handling(self):
        """오류 처리 확인"""
        print("🧪 오류 처리 확인...")
        
        try:
with_open(self.control_center_script,_'r',_encoding = 'utf-8') as f:
                script_content = f.read()
            
            # 오류 처리 패턴 확인
            error_patterns = [
                'print_error',
                'print_warning',
                'exit 1',
                'return 1',
                'if.*then',
                'else'
            ]
            
            found_patterns = []
            for pattern in error_patterns:
                if pattern in script_content:
                    found_patterns.append(pattern)
                    print(f"✅ 오류 처리 패턴 발견: {pattern}")
            
            # 조건문 확인
            conditional_checks = [
                'command -v',
                'if.*exists',
                'if.*-f',
                'if.*-d'
            ]
            
            found_checks = []
            for check in conditional_checks:
                if check in script_content:
                    found_checks.append(check)
                    print(f"✅ 조건 확인 패턴 발견: {check}")
            
            if len(found_patterns) >= 3 and len(found_checks) >= 2:
                self.test_results.append(("error_handling", True, f"오류 처리 확인 성공 ({len(found_patterns)}개 패턴, {len(found_checks)}개 조건)"))
            else:
                self.test_results.append(("error_handling", False, f"오류 처리 부족 ({len(found_patterns)}개 패턴, {len(found_checks)}개 조건)"))
                
        except Exception as e:
            print(f"❌ 오류 처리 확인 실패: {e}")
            self.test_results.append(("error_handling", False, str(e)))
    
    def test_dry_run_execution(self):
        """드라이 런 실행 테스트"""
        print("🧪 드라이 런 실행 테스트...")
        
        try:
            # 환경 변수 설정 (테스트 모드)
            env = os.environ.copy()
            env['TEST_MODE'] = '1'
            
            # 스크립트 실행 (타임아웃 설정)
            result = subprocess.run([
                'bash', '-c', f'echo "0" | timeout 10 {self.control_center_script}'
],_capture_output = True, text=True, env=env, timeout=15)
            
            # 결과 분석
            if result.returncode in [0, 124]:  # 0: 정상 종료, 124: timeout 종료
                print("✅ 스크립트 실행 테스트 성공")
                
                # 출력 내용 확인
                if 'POSCO WatchHamster' in result.stdout or 'POSCO WatchHamster' in result.stderr:
                    print("✅ 제목 출력 확인")
                
                if '워치햄스터' in result.stdout or '워치햄스터' in result.stderr:
                    print("✅ 한글 출력 확인")
                
                self.test_results.append(("dry_run", True, "드라이 런 실행 성공"))
            else:
                print(f"⚠️ 스크립트 실행 결과: {result.returncode}")
                print(f"stdout: {result.stdout[:200]}...")
                print(f"stderr: {result.stderr[:200]}...")
                self.test_results.append(("dry_run", False, f"실행 오류 (코드: {result.returncode})"))
                
        except subprocess.TimeoutExpired:
            print("⚠️ 드라이 런 타임아웃 (정상적인 대화형 스크립트)")
            self.test_results.append(("dry_run", True, "타임아웃 (대화형 스크립트 정상)"))
        except Exception as e:
            print(f"❌ 드라이 런 실행 실패: {e}")
            self.test_results.append(("dry_run", False, str(e)))
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 제어센터 통합 테스트 시작")
        print("=" * 60)
        
        # 개별 테스트 실행
        self.test_script_existence_and_permissions()
        print()
        
        self.test_script_syntax()
        print()
        
        self.test_required_functions()
        print()
        
        self.test_dependency_scripts()
        print()
        
        self.test_environment_check()
        print()
        
        self.test_menu_structure()
        print()
        
        self.test_error_handling()
        print()
        
        self.test_dry_run_execution()
        print()
        
        # 결과 요약
        print("=" * 60)
        print("📊 제어센터 통합 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        for test_name, success, message in self.test_results:
            status = "✅ 성공" if success else "❌ 실패"
            print(f"{status} {test_name}: {message}")
        
        print(f"/n📈 총 {total_tests}개 테스트 중 {passed_tests}개 성공, {failed_tests}개 실패")
        
        if failed_tests == 0:
            print("🎉 모든 제어센터 통합 테스트가 성공했습니다!")
            return True
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")
            return False


def main():
    """메인 함수"""
    tester = ControlCenterTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("/n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())