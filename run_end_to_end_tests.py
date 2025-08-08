#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Test Runner

엔드투엔드 테스트 전용 실행기:
- 전체 시스템 시작/종료 테스트
- 스트레스 테스트 및 부하 테스트
- 실패 시뮬레이션 테스트
- 연속 통합 테스트 스위트

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import os
import sys
import subprocess
import time
import json
import psutil
from datetime import datetime
from typing import Dict, List

class EndToEndTestRunner:
    """엔드투엔드 테스트 실행기"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # 시스템 요구사항 확인
        self.check_system_requirements()
    
    def check_system_requirements(self):
        """시스템 요구사항 확인"""
        print("🔍 시스템 요구사항 확인 중...")
        
        # Python 버전 확인
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            raise RuntimeError(f"Python 3.7 이상이 필요합니다. 현재: {python_version.major}.{python_version.minor}")
        
        print(f"✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 필수 모듈 확인
        required_modules = ['psutil', 'unittest']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ 모듈 확인: {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"❌ 모듈 누락: {module}")
        
        if missing_modules:
            raise RuntimeError(f"필수 모듈이 누락되었습니다: {', '.join(missing_modules)}")
        
        # 시스템 리소스 확인
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        print(f"✅ 메모리: {memory.total // (1024**3)}GB (사용 가능: {memory.available // (1024**3)}GB)")
        print(f"✅ 디스크: {disk.total // (1024**3)}GB (사용 가능: {disk.free // (1024**3)}GB)")
        
        # 최소 요구사항 확인
        if memory.available < 1024**3:  # 1GB
            print("⚠️ 경고: 사용 가능한 메모리가 1GB 미만입니다. 테스트가 실패할 수 있습니다.")
        
        if disk.free < 1024**3:  # 1GB
            print("⚠️ 경고: 사용 가능한 디스크 공간이 1GB 미만입니다.")
    
    def run_test_category(self, category_name: str, timeout: int = 300) -> Dict:
        """테스트 카테고리 실행"""
        print(f"\n{'='*60}")
        print(f"🧪 {category_name} 실행 중...")
        print(f"{'='*60}")
        
        test_script = os.path.join(self.script_dir, 'test_end_to_end_integration.py')
        
        if not os.path.exists(test_script):
            return {
                'category': category_name,
                'success': False,
                'error': f"테스트 스크립트를 찾을 수 없습니다: {test_script}",
                'duration': 0,
                'details': {}
            }
        
        start_time = time.time()
        
        try:
            # 환경 변수 설정
            env = os.environ.copy()
            env['TEST_CATEGORY'] = category_name
            env['TEST_MODE'] = '1'
            
            # 테스트 실행
            result = subprocess.run([
                sys.executable, test_script
            ], capture_output=True, text=True, timeout=timeout, 
            cwd=self.script_dir, env=env)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 결과 분석
            success = result.returncode == 0
            
            # 출력에서 테스트 통계 추출
            test_stats = self.parse_test_output(result.stdout)
            
            test_result = {
                'category': category_name,
                'success': success,
                'return_code': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'details': test_stats
            }
            
            if success:
                print(f"✅ {category_name} 성공 (소요시간: {duration:.2f}초)")
            else:
                print(f"❌ {category_name} 실패 (return code: {result.returncode})")
                if result.stderr:
                    print(f"오류: {result.stderr[:500]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ {category_name} 타임아웃 ({timeout}초)")
            
            return {
                'category': category_name,
                'success': False,
                'error': f"테스트 타임아웃 ({timeout}초)",
                'duration': duration,
                'details': {}
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"❌ {category_name} 실행 중 오류: {e}")
            
            return {
                'category': category_name,
                'success': False,
                'error': str(e),
                'duration': duration,
                'details': {}
            }
    
    def parse_test_output(self, output: str) -> Dict:
        """테스트 출력 파싱"""
        stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'success_rate': 0.0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # unittest 출력 패턴 찾기
            if 'Ran' in line and 'test' in line:
                try:
                    # "Ran X tests in Y.Zs" 패턴
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == 'Ran':
                        stats['total_tests'] = int(parts[1])
                except (ValueError, IndexError):
                    pass
            
            elif 'FAILED' in line and 'failures' in line:
                try:
                    # "FAILED (failures=X, errors=Y)" 패턴
                    if 'failures=' in line:
                        failures_part = line.split('failures=')[1].split(',')[0].split(')')[0]
                        stats['failed_tests'] = int(failures_part)
                    
                    if 'errors=' in line:
                        errors_part = line.split('errors=')[1].split(',')[0].split(')')[0]
                        stats['error_tests'] = int(errors_part)
                except (ValueError, IndexError):
                    pass
            
            elif 'OK' in line and stats['total_tests'] > 0:
                # 모든 테스트가 성공한 경우
                stats['passed_tests'] = stats['total_tests']
        
        # 성공한 테스트 수 계산
        if stats['passed_tests'] == 0 and stats['total_tests'] > 0:
            stats['passed_tests'] = stats['total_tests'] - stats['failed_tests'] - stats['error_tests']
        
        # 성공률 계산
        if stats['total_tests'] > 0:
            stats['success_rate'] = (stats['passed_tests'] / stats['total_tests']) * 100
        
        return stats
    
    def generate_comprehensive_report(self) -> str:
        """종합 보고서 생성"""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # 전체 통계 계산
        total_categories = len(self.test_results)
        successful_categories = sum(1 for r in self.test_results.values() if r['success'])
        
        total_tests = sum(r['details'].get('total_tests', 0) for r in self.test_results.values())
        total_passed = sum(r['details'].get('passed_tests', 0) for r in self.test_results.values())
        total_failed = sum(r['details'].get('failed_tests', 0) for r in self.test_results.values())
        total_errors = sum(r['details'].get('error_tests', 0) for r in self.test_results.values())
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
🎯 POSCO WatchHamster v2 엔드투엔드 통합 테스트 보고서
{'='*80}

📊 실행 요약
• 시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
• 종료 시간: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}
• 총 소요 시간: {total_duration:.2f}초

📈 카테고리별 결과
• 총 카테고리: {total_categories}개
• 성공한 카테고리: {successful_categories}개
• 실패한 카테고리: {total_categories - successful_categories}개
• 카테고리 성공률: {(successful_categories/total_categories*100):.1f}%

📋 개별 테스트 통계
• 총 테스트: {total_tests}개
• 성공: {total_passed}개
• 실패: {total_failed}개
• 오류: {total_errors}개
• 전체 성공률: {overall_success_rate:.1f}%

{'='*80}
📋 상세 결과
{'='*80}
"""
        
        for category, result in self.test_results.items():
            status = "✅ 성공" if result['success'] else "❌ 실패"
            details = result['details']
            
            report += f"""
{status} {category}
• 소요시간: {result['duration']:.2f}초
• 개별 테스트: {details.get('total_tests', 0)}개
• 성공: {details.get('passed_tests', 0)}개
• 실패: {details.get('failed_tests', 0)}개
• 오류: {details.get('error_tests', 0)}개
• 성공률: {details.get('success_rate', 0):.1f}%
"""
            
            if not result['success']:
                error_msg = result.get('error', 'Unknown error')
                report += f"• 오류 메시지: {error_msg}\n"
        
        # 권장사항
        report += f"""
{'='*80}
🔧 권장사항 및 다음 단계
{'='*80}
"""
        
        if successful_categories == total_categories and overall_success_rate >= 90:
            report += """
✅ 모든 엔드투엔드 테스트가 성공했습니다!

🎉 시스템 상태: 우수
• v2 통합 시스템이 모든 시나리오에서 안정적으로 동작합니다.
• 스트레스 테스트와 실패 시뮬레이션을 모두 통과했습니다.
• 프로덕션 환경 배포 준비가 완료되었습니다.

📋 다음 단계:
• 프로덕션 환경으로 배포 진행
• 정기적인 회귀 테스트 스케줄 설정
• 모니터링 시스템 활성화
"""
        elif successful_categories >= total_categories * 0.8:
            report += f"""
⚠️ 대부분의 테스트가 성공했지만 일부 개선이 필요합니다.

📊 시스템 상태: 양호 (성공률: {overall_success_rate:.1f}%)
• 핵심 기능은 정상 동작하지만 일부 최적화가 필요합니다.
• 실패한 테스트를 검토하고 수정하세요.

📋 다음 단계:
• 실패한 테스트 케이스 분석 및 수정
• 성능 최적화 작업 수행
• 수정 후 재테스트 실행
"""
        else:
            report += f"""
❌ 다수의 테스트가 실패했습니다. 시스템 점검이 필요합니다.

🔴 시스템 상태: 불안정 (성공률: {overall_success_rate:.1f}%)
• 핵심 기능에 문제가 있을 수 있습니다.
• 프로덕션 배포 전 반드시 문제를 해결하세요.

📋 다음 단계:
• 실패한 모든 테스트 케이스 우선 분석
• 시스템 아키텍처 재검토
• 단계별 수정 및 검증 수행
• 전체 테스트 재실행
"""
        
        report += f"""
📁 상세 로그
• 테스트 실행 디렉토리: {self.script_dir}
• 개별 테스트 출력은 각 카테고리별로 확인 가능
• 실패한 테스트의 상세 오류는 stderr 출력 참조

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def save_test_results(self):
        """테스트 결과를 JSON 파일로 저장"""
        results_file = os.path.join(self.script_dir, 'end_to_end_test_results.json')
        
        # 결과 데이터 준비
        test_session = {
            'session_start': self.start_time.isoformat(),
            'session_end': self.end_time.isoformat(),
            'total_duration': (self.end_time - self.start_time).total_seconds(),
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_free': psutil.disk_usage('.').free
            },
            'results': {}
        }
        
        # 결과 데이터 직렬화
        for category, result in self.test_results.items():
            serializable_result = result.copy()
            # stdout/stderr는 너무 클 수 있으므로 요약만 저장
            if 'stdout' in serializable_result:
                serializable_result['stdout_length'] = len(serializable_result['stdout'])
                del serializable_result['stdout']
            if 'stderr' in serializable_result:
                serializable_result['stderr_length'] = len(serializable_result['stderr'])
                del serializable_result['stderr']
            
            test_session['results'][category] = serializable_result
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(test_session, f, indent=2, ensure_ascii=False)
            
            print(f"📁 테스트 결과 저장: {results_file}")
            
        except Exception as e:
            print(f"⚠️ 테스트 결과 저장 실패: {e}")
    
    def run_all_tests(self) -> bool:
        """모든 엔드투엔드 테스트 실행"""
        self.start_time = datetime.now()
        
        print("🚀 POSCO WatchHamster v2 엔드투엔드 통합 테스트 프레임워크")
        print("="*80)
        print(f"시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 테스트 카테고리 정의
        test_categories = [
            ("전체 시스템 테스트", 180),
            ("스트레스 테스트", 300),
            ("실패 시뮬레이션 테스트", 240),
            ("연속 통합 테스트", 360)
        ]
        
        # 각 카테고리별 테스트 실행
        for category_name, timeout in test_categories:
            result = self.run_test_category(category_name, timeout)
            self.test_results[category_name] = result
            
            # 중간 결과 출력
            if result['success']:
                print(f"✅ {category_name} 완료")
            else:
                print(f"❌ {category_name} 실패")
            
            print()
        
        self.end_time = datetime.now()
        
        # 종합 보고서 생성 및 출력
        print("="*80)
        print("📊 엔드투엔드 통합 테스트 최종 결과")
        print("="*80)
        
        comprehensive_report = self.generate_comprehensive_report()
        print(comprehensive_report)
        
        # 결과 저장
        self.save_test_results()
        
        # 전체 성공 여부 판단
        successful_categories = sum(1 for r in self.test_results.values() if r['success'])
        total_categories = len(self.test_results)
        success_rate = (successful_categories / total_categories * 100) if total_categories > 0 else 0
        
        # 80% 이상 성공 시 전체 성공으로 간주
        return success_rate >= 80.0


def main():
    """메인 함수"""
    runner = EndToEndTestRunner()
    
    try:
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 엔드투엔드 통합 테스트가 성공적으로 완료되었습니다!")
            return 0
        else:
            print("\n❌ 엔드투엔드 통합 테스트에서 문제가 발견되었습니다.")
            print("상세한 내용은 위의 보고서를 참조하세요.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        return 1
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())