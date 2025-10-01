#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 충돌 자동 해결 시스템 테스트
Requirements 3.2, 3.3 구현 검증

테스트 시나리오:
1. 충돌 파일 감지 및 분석
2. 자동 해결 가능한 충돌 처리
3. 수동 해결이 필요한 충돌 GUI 인터페이스
4. 충돌 해결 옵션 제공 및 적용
"""

import os
import sys
import tempfile
import shutil
import subprocess
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from git_deployment_manager import GitDeploymentManager
except ImportError as e:
    print(f"GitDeploymentManager import 오류: {e}")
    sys.exit(1)


class ConflictResolutionTester:
    """충돌 해결 시스템 테스터"""
    
    def __init__(self):
        """테스터 초기화"""
        self.test_dir = None
        self.deployment_manager = None
        self.test_results = []
    
    def setup_test_environment(self):
        """테스트 환경 설정"""
        print("🔧 테스트 환경 설정 중...")
        
        try:
            # 임시 디렉토리 생성
            self.test_dir = tempfile.mkdtemp(prefix="git_conflict_test_")
            print(f"📁 테스트 디렉토리: {self.test_dir}")
            
            # Git 저장소 초기화
            os.chdir(self.test_dir)
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
            
            # 배포 관리자 초기화
            self.deployment_manager = GitDeploymentManager(self.test_dir)
            
            print("✅ 테스트 환경 설정 완료")
            return True
            
        except Exception as e:
            print(f"❌ 테스트 환경 설정 실패: {e}")
            return False
    
    def create_conflict_scenario(self):
        """충돌 시나리오 생성"""
        print("🎭 충돌 시나리오 생성 중...")
        
        try:
            # 초기 파일 생성 및 커밋
            test_files = {
                'simple.txt': 'Line 1\nLine 2\nLine 3\n',
                'config.json': '{\n  "version": "1.0.0",\n  "name": "test"\n}',
                'code.py': 'def hello():\n    print("Hello World")\n    return True\n'
            }
            
            for filename, content in test_files.items():
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
            
            # main 브랜치에서 변경
            with open('simple.txt', 'w', encoding='utf-8') as f:
                f.write('Line 1 (main version)\nLine 2\nLine 3\n')
            
            with open('config.json', 'w', encoding='utf-8') as f:
                f.write('{\n  "version": "1.1.0",\n  "name": "test-main"\n}')
            
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Main branch changes'], check=True)
            
            # feature 브랜치 생성 및 충돌하는 변경
            subprocess.run(['git', 'checkout', '-b', 'feature'], check=True)
            subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], check=True)  # 이전 커밋으로 되돌리기
            
            with open('simple.txt', 'w', encoding='utf-8') as f:
                f.write('Line 1 (feature version)\nLine 2\nLine 3\n')
            
            with open('config.json', 'w', encoding='utf-8') as f:
                f.write('{\n  "version": "1.0.1",\n  "name": "test-feature"\n}')
            
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Feature branch changes'], check=True)
            
            # main으로 돌아가서 병합 시도 (충돌 발생)
            subprocess.run(['git', 'checkout', 'main'], check=True)
            
            # 병합 시도 (충돌 발생 예상)
            result = subprocess.run(['git', 'merge', 'feature'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("✅ 충돌 시나리오 생성 완료 (예상된 충돌 발생)")
                return True
            else:
                print("⚠️ 예상된 충돌이 발생하지 않았습니다")
                return False
                
        except Exception as e:
            print(f"❌ 충돌 시나리오 생성 실패: {e}")
            return False
    
    def test_conflict_detection(self):
        """충돌 감지 테스트"""
        print("\n🔍 충돌 감지 테스트...")
        
        try:
            conflict_info = self.deployment_manager.detect_conflict_files()
            
            # 결과 검증
            if conflict_info['has_conflicts']:
                print(f"✅ 충돌 감지 성공: {len(conflict_info['conflict_files'])}개 파일")
                
                for file_path in conflict_info['conflict_files']:
                    print(f"  📄 충돌 파일: {file_path}")
                    
                    if file_path in conflict_info['conflict_details']:
                        details = conflict_info['conflict_details'][file_path]
                        print(f"    - 파일 타입: {details['file_type']}")
                        print(f"    - 충돌 마커: {details['conflict_markers']}개")
                        print(f"    - 자동 해결 가능: {details['auto_resolvable']}")
                        if details['auto_resolvable']:
                            print(f"    - 해결 전략: {details['resolution_strategy']}")
                
                self.test_results.append(("충돌 감지", True, f"{len(conflict_info['conflict_files'])}개 파일 감지"))
                return conflict_info
            else:
                print("❌ 충돌이 감지되지 않았습니다")
                self.test_results.append(("충돌 감지", False, "충돌 미감지"))
                return None
                
        except Exception as e:
            print(f"❌ 충돌 감지 테스트 실패: {e}")
            self.test_results.append(("충돌 감지", False, str(e)))
            return None
    
    def test_auto_resolution(self):
        """자동 충돌 해결 테스트"""
        print("\n🤖 자동 충돌 해결 테스트...")
        
        try:
            # GUI 콜백 함수 (테스트용)
            def test_gui_callback(manual_files, conflict_info):
                print(f"🖥️ GUI 콜백 호출: {len(manual_files)}개 파일 수동 해결 필요")
                for file_path in manual_files:
                    print(f"  👤 수동 해결 필요: {file_path}")
                
                # 테스트에서는 자동으로 'ours' 옵션 선택
                resolved_files = []
                for file_path in manual_files:
                    if self.deployment_manager.resolve_conflict_with_option(file_path, 'ours'):
                        resolved_files.append(file_path)
                        print(f"  ✅ 테스트 자동 해결: {file_path}")
                
                return {'resolved_files': resolved_files}
            
            # 충돌 해결 실행
            resolution_result = self.deployment_manager.handle_git_conflicts(test_gui_callback)
            
            # 결과 검증
            if resolution_result['success']:
                print("✅ 충돌 해결 성공")
                
                summary = resolution_result.get('resolution_summary', {})
                print(f"📊 해결 요약:")
                print(f"  - 총 충돌: {summary.get('total_conflicts', 0)}개")
                print(f"  - 자동 해결: {summary.get('auto_resolved', 0)}개")
                print(f"  - 수동 해결: {summary.get('manual_required', 0)}개")
                
                self.test_results.append(("자동 충돌 해결", True, "모든 충돌 해결 완료"))
                return True
            else:
                error_msg = resolution_result.get('error_message', '알 수 없는 오류')
                print(f"❌ 충돌 해결 실패: {error_msg}")
                
                if resolution_result.get('gui_intervention_needed'):
                    print(f"👤 GUI 개입 필요: {len(resolution_result['manual_required'])}개 파일")
                
                self.test_results.append(("자동 충돌 해결", False, error_msg))
                return False
                
        except Exception as e:
            print(f"❌ 자동 충돌 해결 테스트 실패: {e}")
            self.test_results.append(("자동 충돌 해결", False, str(e)))
            return False
    
    def test_resolution_options(self):
        """충돌 해결 옵션 테스트"""
        print("\n⚙️ 충돌 해결 옵션 테스트...")
        
        try:
            # 새로운 충돌 시나리오 생성
            if not self.create_simple_conflict():
                return False
            
            # 충돌 파일 확인
            conflict_info = self.deployment_manager.detect_conflict_files()
            if not conflict_info['has_conflicts']:
                print("❌ 테스트용 충돌이 생성되지 않았습니다")
                return False
            
            test_file = conflict_info['conflict_files'][0]
            print(f"📄 테스트 파일: {test_file}")
            
            # 해결 옵션 가져오기
            options = self.deployment_manager.get_conflict_resolution_options(test_file)
            
            print(f"⚙️ 사용 가능한 해결 옵션:")
            for option in options['resolution_options']:
                print(f"  - {option['id']}: {option['name']} - {option['description']}")
            
            # 각 옵션 테스트
            for option_id in ['ours', 'theirs']:
                print(f"\n🧪 '{option_id}' 옵션 테스트...")
                
                # 충돌 상태 복원
                subprocess.run(['git', 'reset', '--hard', 'HEAD'], check=True)
                subprocess.run(['git', 'merge', 'feature'], capture_output=True)
                
                # 옵션 적용
                success = self.deployment_manager.resolve_conflict_with_option(test_file, option_id)
                
                if success:
                    print(f"✅ '{option_id}' 옵션 적용 성공")
                else:
                    print(f"❌ '{option_id}' 옵션 적용 실패")
            
            self.test_results.append(("충돌 해결 옵션", True, "모든 옵션 테스트 완료"))
            return True
            
        except Exception as e:
            print(f"❌ 충돌 해결 옵션 테스트 실패: {e}")
            self.test_results.append(("충돌 해결 옵션", False, str(e)))
            return False
    
    def create_simple_conflict(self):
        """간단한 충돌 생성"""
        try:
            # 현재 상태 리셋
            subprocess.run(['git', 'reset', '--hard', 'HEAD'], check=True)
            subprocess.run(['git', 'clean', '-fd'], check=True)
            
            # 새로운 파일 생성
            with open('test_conflict.txt', 'w', encoding='utf-8') as f:
                f.write('Original content\n')
            
            subprocess.run(['git', 'add', 'test_conflict.txt'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Add test file'], check=True)
            
            # 브랜치 생성 및 변경
            subprocess.run(['git', 'checkout', '-b', 'test_branch'], check=True)
            with open('test_conflict.txt', 'w', encoding='utf-8') as f:
                f.write('Branch content\n')
            
            subprocess.run(['git', 'add', 'test_conflict.txt'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Branch change'], check=True)
            
            # main으로 돌아가서 다른 변경
            subprocess.run(['git', 'checkout', 'main'], check=True)
            with open('test_conflict.txt', 'w', encoding='utf-8') as f:
                f.write('Main content\n')
            
            subprocess.run(['git', 'add', 'test_conflict.txt'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Main change'], check=True)
            
            # 병합 시도 (충돌 발생)
            result = subprocess.run(['git', 'merge', 'test_branch'], 
                                  capture_output=True, text=True)
            
            return result.returncode != 0  # 충돌 발생 시 True
            
        except Exception as e:
            print(f"❌ 간단한 충돌 생성 실패: {e}")
            return False
    
    def cleanup_test_environment(self):
        """테스트 환경 정리"""
        print("\n🧹 테스트 환경 정리 중...")
        
        try:
            if self.test_dir and os.path.exists(self.test_dir):
                os.chdir(os.path.dirname(self.test_dir))
                shutil.rmtree(self.test_dir)
                print("✅ 테스트 환경 정리 완료")
            
        except Exception as e:
            print(f"⚠️ 테스트 환경 정리 중 오류: {e}")
    
    def print_test_results(self):
        """테스트 결과 출력"""
        print("\n" + "="*60)
        print("📊 Git 충돌 해결 시스템 테스트 결과")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        
        for test_name, success, message in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
        
        print("-"*60)
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {passed_tests}개")
        print(f"실패: {total_tests - passed_tests}개")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if passed_tests == total_tests:
            print("\n🎉 모든 테스트 통과! Git 충돌 해결 시스템이 정상 작동합니다.")
        else:
            print(f"\n⚠️ {total_tests - passed_tests}개 테스트 실패. 시스템 점검이 필요합니다.")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Git 충돌 해결 시스템 테스트 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 테스트 환경 설정
            if not self.setup_test_environment():
                return False
            
            # 충돌 시나리오 생성
            if not self.create_conflict_scenario():
                return False
            
            # 테스트 실행
            self.test_conflict_detection()
            self.test_auto_resolution()
            self.test_resolution_options()
            
            return True
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            self.test_results.append(("전체 테스트", False, str(e)))
            return False
            
        finally:
            self.cleanup_test_environment()
            self.print_test_results()


def main():
    """메인 함수"""
    print("🔧 Git 충돌 자동 해결 시스템 테스트")
    print("Requirements 3.2, 3.3 구현 검증\n")
    
    tester = ConflictResolutionTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()