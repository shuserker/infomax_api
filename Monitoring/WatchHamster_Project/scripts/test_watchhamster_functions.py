#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워치햄스터 레벨 기능 테스트 스크립트

이 스크립트는 다음 기능들을 테스트합니다:
- 워치햄스터 모니터 모듈 로드 테스트
- Git 모니터링 기능 테스트  
- 시스템 리소스 모니터링 테스트

Requirements: 3.1, 3.2
"""

import sys
import os
import json
import traceback
from datetime import datetime
from typing import Dict, Any, List

# 워치햄스터 프로젝트 경로를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

class WatchHamsterFunctionTester:
    """워치햄스터 기능 테스트 클래스"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'overall_status': 'unknown'
        }
        
    def log_test_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """테스트 결과 로깅"""
        self.test_results['total_tests'] += 1
        
        if success:
            self.test_results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ FAIL"
            
        result_entry = {
            'test_name': test_name,
            'status': status,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            result_entry['details'] = details
            
        self.test_results['test_details'].append(result_entry)
        
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    세부사항: {details}")
    
    def test_module_imports(self) -> bool:
        """모듈 import 테스트"""
        print("\n=== 1. 모듈 Import 테스트 ===")
        
        # 워치햄스터 모니터 모듈 import 테스트
        try:
            from core.watchhamster_monitor import WatchHamsterMonitor, ProcessStatus, SystemResourceLevel
            self.log_test_result(
                "워치햄스터 모니터 모듈 import",
                True,
                "워치햄스터 모니터 모듈이 성공적으로 로드되었습니다"
            )
        except Exception as e:
            self.log_test_result(
                "워치햄스터 모니터 모듈 import",
                False,
                f"워치햄스터 모니터 모듈 로드 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
        
        # Git 모니터 모듈 import 테스트
        try:
            from core.git_monitor import GitMonitor, GitStatus
            self.log_test_result(
                "Git 모니터 모듈 import",
                True,
                "Git 모니터 모듈이 성공적으로 로드되었습니다"
            )
        except Exception as e:
            self.log_test_result(
                "Git 모니터 모듈 import",
                False,
                f"Git 모니터 모듈 로드 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
            
        return True
    
    def test_watchhamster_monitor_initialization(self) -> bool:
        """워치햄스터 모니터 초기화 테스트"""
        print("\n=== 2. 워치햄스터 모니터 초기화 테스트 ===")
        
        try:
            from core.watchhamster_monitor import WatchHamsterMonitor
            
            # 테스트용 설정
            test_config = {
                'process_check_interval': 60,
                'git_check_interval': 300,
                'status_notification_interval': 1800,
                'managed_processes': ['python', 'test_process'],
                'max_restart_attempts': 3,
                'restart_cooldown': 30,
                'webhook_url': 'https://test.webhook.url',
                'bot_profile_image': 'test_image.jpg'
            }
            
            # 워치햄스터 모니터 인스턴스 생성
            monitor = WatchHamsterMonitor(test_config)
            
            # 초기화 검증
            if hasattr(monitor, 'config') and hasattr(monitor, 'managed_processes'):
                self.log_test_result(
                    "워치햄스터 모니터 초기화",
                    True,
                    f"워치햄스터 모니터가 성공적으로 초기화되었습니다 (관리 프로세스: {len(monitor.managed_processes)}개)",
                    {
                        'managed_processes': monitor.managed_processes,
                        'process_check_interval': monitor.process_check_interval,
                        'git_check_interval': monitor.git_check_interval
                    }
                )
                return True
            else:
                self.log_test_result(
                    "워치햄스터 모니터 초기화",
                    False,
                    "워치햄스터 모니터 초기화 후 필수 속성이 누락되었습니다"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "워치햄스터 모니터 초기화",
                False,
                f"워치햄스터 모니터 초기화 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_process_monitoring(self) -> bool:
        """프로세스 모니터링 기능 테스트"""
        print("\n=== 3. 프로세스 모니터링 기능 테스트 ===")
        
        try:
            from core.watchhamster_monitor import WatchHamsterMonitor
            
            # 테스트용 설정 (실제 존재하는 프로세스 포함)
            test_config = {
                'managed_processes': ['python', 'kernel_task'],  # macOS에서 일반적으로 존재하는 프로세스들
                'process_check_interval': 60
            }
            
            monitor = WatchHamsterMonitor(test_config)
            
            # 프로세스 모니터링 실행
            monitoring_results = monitor.monitor_processes()
            
            # 결과 검증
            required_keys = ['timestamp', 'total_processes', 'healthy_processes', 'process_details', 'system_health']
            missing_keys = [key for key in required_keys if key not in monitoring_results]
            
            if missing_keys:
                self.log_test_result(
                    "프로세스 모니터링 결과 구조",
                    False,
                    f"모니터링 결과에 필수 키가 누락되었습니다: {missing_keys}"
                )
                return False
            
            # 프로세스 세부 정보 검증
            process_details = monitoring_results.get('process_details', {})
            if not process_details:
                self.log_test_result(
                    "프로세스 세부 정보",
                    False,
                    "프로세스 세부 정보가 비어있습니다"
                )
                return False
            
            self.log_test_result(
                "프로세스 모니터링 기능",
                True,
                f"프로세스 모니터링이 성공적으로 실행되었습니다 (총 {monitoring_results['total_processes']}개 프로세스, {monitoring_results['healthy_processes']}개 정상)",
                {
                    'total_processes': monitoring_results['total_processes'],
                    'healthy_processes': monitoring_results['healthy_processes'],
                    'system_health': monitoring_results['system_health'],
                    'process_names': list(process_details.keys())
                }
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "프로세스 모니터링 기능",
                False,
                f"프로세스 모니터링 실행 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_git_monitoring(self) -> bool:
        """Git 모니터링 기능 테스트"""
        print("\n=== 4. Git 모니터링 기능 테스트 ===")
        
        try:
            from core.git_monitor import GitMonitor
            
            # Git 모니터 인스턴스 생성
            git_monitor = GitMonitor(repo_path=".")
            
            # Git 저장소 확인
            is_git_repo = git_monitor.check_git_repository()
            
            if not is_git_repo:
                self.log_test_result(
                    "Git 저장소 확인",
                    False,
                    "현재 디렉토리가 Git 저장소가 아닙니다",
                    {'repo_path': os.getcwd()}
                )
                return False
            
            self.log_test_result(
                "Git 저장소 확인",
                True,
                "Git 저장소가 정상적으로 감지되었습니다"
            )
            
            # Git 상태 확인
            git_status = git_monitor.get_git_status()
            
            if git_status.status == "오류":
                self.log_test_result(
                    "Git 상태 확인",
                    False,
                    f"Git 상태 확인 실패: {git_status.error_message}"
                )
                return False
            
            self.log_test_result(
                "Git 상태 확인",
                True,
                f"Git 상태가 성공적으로 확인되었습니다 (브랜치: {git_status.branch}, 상태: {git_status.status})",
                {
                    'branch': git_status.branch,
                    'status': git_status.status,
                    'last_commit': git_status.last_commit,
                    'uncommitted_changes': git_status.uncommitted_changes
                }
            )
            
            # 저장소 건강 상태 검사
            health_report = git_monitor.check_repository_health()
            
            if not health_report['repository_valid']:
                self.log_test_result(
                    "Git 저장소 건강 상태",
                    False,
                    "Git 저장소 건강 상태 검사 실패",
                    health_report
                )
                return False
            
            self.log_test_result(
                "Git 저장소 건강 상태",
                True,
                f"Git 저장소 건강 상태 검사 완료 (문제점: {len(health_report['issues'])}개)",
                {
                    'issues_count': len(health_report['issues']),
                    'recommendations_count': len(health_report['recommendations']),
                    'conflicts_count': len(health_report['conflicts'])
                }
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Git 모니터링 기능",
                False,
                f"Git 모니터링 실행 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_system_resource_monitoring(self) -> bool:
        """시스템 리소스 모니터링 테스트"""
        print("\n=== 5. 시스템 리소스 모니터링 테스트 ===")
        
        try:
            from core.watchhamster_monitor import WatchHamsterMonitor
            
            # 테스트용 설정
            test_config = {
                'managed_processes': ['python']
            }
            
            monitor = WatchHamsterMonitor(test_config)
            
            # 시스템 리소스 모니터링 실행
            resource_status = monitor.monitor_system_resources()
            
            # 결과 검증
            required_keys = ['timestamp', 'cpu', 'memory', 'disk', 'overall_level']
            missing_keys = [key for key in required_keys if key not in resource_status]
            
            if missing_keys:
                self.log_test_result(
                    "시스템 리소스 모니터링 결과 구조",
                    False,
                    f"리소스 모니터링 결과에 필수 키가 누락되었습니다: {missing_keys}"
                )
                return False
            
            # CPU 정보 검증
            cpu_info = resource_status.get('cpu', {})
            if 'percent' not in cpu_info or 'level' not in cpu_info:
                self.log_test_result(
                    "CPU 모니터링 정보",
                    False,
                    "CPU 모니터링 정보가 불완전합니다"
                )
                return False
            
            # 메모리 정보 검증
            memory_info = resource_status.get('memory', {})
            if 'percent' not in memory_info or 'available_gb' not in memory_info:
                self.log_test_result(
                    "메모리 모니터링 정보",
                    False,
                    "메모리 모니터링 정보가 불완전합니다"
                )
                return False
            
            # 디스크 정보 검증
            disk_info = resource_status.get('disk', {})
            if 'percent' not in disk_info or 'free_gb' not in disk_info:
                self.log_test_result(
                    "디스크 모니터링 정보",
                    False,
                    "디스크 모니터링 정보가 불완전합니다"
                )
                return False
            
            self.log_test_result(
                "시스템 리소스 모니터링",
                True,
                f"시스템 리소스 모니터링이 성공적으로 실행되었습니다 (전체 레벨: {resource_status['overall_level']})",
                {
                    'cpu_percent': cpu_info['percent'],
                    'memory_percent': memory_info['percent'],
                    'disk_percent': disk_info['percent'],
                    'overall_level': resource_status['overall_level'],
                    'warnings_count': len(resource_status.get('warnings', [])),
                    'critical_issues_count': len(resource_status.get('critical_issues', []))
                }
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "시스템 리소스 모니터링",
                False,
                f"시스템 리소스 모니터링 실행 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_system_monitor_module(self) -> bool:
        """시스템 모니터 모듈 독립 테스트"""
        print("\n=== 6. 시스템 모니터 모듈 테스트 ===")
        
        try:
            from core.system_monitor import SystemMonitor, ResourceLevel
            
            # 시스템 모니터 인스턴스 생성
            system_monitor = SystemMonitor()
            
            # 전체 시스템 리소스 상태 확인
            resource_status = system_monitor.get_system_resource_status()
            
            # 결과 검증
            if not hasattr(resource_status, 'cpu') or not hasattr(resource_status, 'memory'):
                self.log_test_result(
                    "시스템 모니터 모듈 기본 기능",
                    False,
                    "시스템 리소스 상태 객체가 올바르지 않습니다"
                )
                return False
            
            # CPU 정보 검증
            if resource_status.cpu.percent < 0 or resource_status.cpu.percent > 100:
                self.log_test_result(
                    "CPU 정보 유효성",
                    False,
                    f"CPU 사용률이 유효하지 않습니다: {resource_status.cpu.percent}%"
                )
                return False
            
            # 메모리 정보 검증
            if resource_status.memory.percent < 0 or resource_status.memory.percent > 100:
                self.log_test_result(
                    "메모리 정보 유효성",
                    False,
                    f"메모리 사용률이 유효하지 않습니다: {resource_status.memory.percent}%"
                )
                return False
            
            # 알림 메시지 생성 테스트
            alert_message = system_monitor.generate_resource_alert(resource_status)
            
            if not alert_message or len(alert_message) < 50:
                self.log_test_result(
                    "시스템 모니터 알림 메시지",
                    False,
                    "시스템 모니터 알림 메시지가 너무 짧거나 비어있습니다"
                )
                return False
            
            self.log_test_result(
                "시스템 모니터 모듈",
                True,
                f"시스템 모니터 모듈이 성공적으로 작동합니다 (CPU: {resource_status.cpu.percent:.1f}%, 메모리: {resource_status.memory.percent:.1f}%)",
                {
                    'cpu_percent': resource_status.cpu.percent,
                    'memory_percent': resource_status.memory.percent,
                    'disk_percent': resource_status.disk.percent,
                    'overall_level': resource_status.overall_level.value,
                    'top_processes_count': len(resource_status.top_processes)
                }
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "시스템 모니터 모듈",
                False,
                f"시스템 모니터 모듈 테스트 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_alert_message_generation(self) -> bool:
        """알림 메시지 생성 테스트"""
        print("\n=== 7. 알림 메시지 생성 테스트 ===")
        
        try:
            from core.watchhamster_monitor import WatchHamsterMonitor
            
            # 테스트용 설정
            test_config = {
                'managed_processes': ['python']
            }
            
            monitor = WatchHamsterMonitor(test_config)
            
            # 테스트용 데이터 생성
            test_process_results = {
                'healthy_processes': 2,
                'total_processes': 3,
                'failed_processes': ['test_process']
            }
            
            test_git_status = {
                'status': 'clean',
                'current_branch': 'main',
                'current_commit': 'abc12345'
            }
            
            test_resource_status = {
                'overall_level': 'normal',
                'cpu': {'percent': 25.5},
                'memory': {'percent': 45.2},
                'disk': {'percent': 60.1}
            }
            
            # 알림 메시지 생성 테스트
            alert_message = monitor.generate_dynamic_alert_message(
                test_process_results,
                test_git_status,
                test_resource_status,
                "status"
            )
            
            if not alert_message or len(alert_message) < 50:
                self.log_test_result(
                    "알림 메시지 생성",
                    False,
                    "생성된 알림 메시지가 너무 짧거나 비어있습니다"
                )
                return False
            
            # 메시지에 필수 정보가 포함되어 있는지 확인
            required_elements = ['POSCO', '워치햄스터', '시간:', '프로세스']
            missing_elements = [elem for elem in required_elements if elem not in alert_message]
            
            if missing_elements:
                self.log_test_result(
                    "알림 메시지 내용 검증",
                    False,
                    f"알림 메시지에 필수 요소가 누락되었습니다: {missing_elements}"
                )
                return False
            
            self.log_test_result(
                "알림 메시지 생성",
                True,
                f"알림 메시지가 성공적으로 생성되었습니다 (길이: {len(alert_message)}자)",
                {
                    'message_length': len(alert_message),
                    'contains_required_elements': True,
                    'message_preview': alert_message[:100] + "..." if len(alert_message) > 100 else alert_message
                }
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "알림 메시지 생성",
                False,
                f"알림 메시지 생성 실패: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("🐹 워치햄스터 레벨 기능 테스트 시작")
        print("=" * 60)
        
        # 테스트 실행
        tests = [
            self.test_module_imports,
            self.test_watchhamster_monitor_initialization,
            self.test_process_monitoring,
            self.test_git_monitoring,
            self.test_system_resource_monitoring,
            self.test_system_monitor_module,
            self.test_alert_message_generation
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test_result(
                    f"{test_func.__name__}",
                    False,
                    f"테스트 실행 중 예외 발생: {str(e)}",
                    {'error': str(e), 'traceback': traceback.format_exc()}
                )
        
        # 전체 결과 계산
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            
            if success_rate == 100:
                self.test_results['overall_status'] = 'excellent'
            elif success_rate >= 80:
                self.test_results['overall_status'] = 'good'
            elif success_rate >= 60:
                self.test_results['overall_status'] = 'warning'
            else:
                self.test_results['overall_status'] = 'critical'
        else:
            self.test_results['overall_status'] = 'no_tests'
        
        # 결과 출력
        print("\n" + "=" * 60)
        print("🏁 워치햄스터 레벨 기능 테스트 완료")
        print("=" * 60)
        print(f"📊 총 테스트: {self.test_results['total_tests']}개")
        print(f"✅ 성공: {self.test_results['passed_tests']}개")
        print(f"❌ 실패: {self.test_results['failed_tests']}개")
        
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"📈 성공률: {success_rate:.1f}%")
        
        print(f"🎯 전체 상태: {self.test_results['overall_status']}")
        
        # 실패한 테스트 요약
        failed_tests = [test for test in self.test_results['test_details'] if not test['success']]
        if failed_tests:
            print(f"\n❌ 실패한 테스트 ({len(failed_tests)}개):")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['message']}")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """테스트 결과를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"watchhamster_function_test_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 테스트 결과가 저장되었습니다: {filepath}")
        except Exception as e:
            print(f"\n❌ 테스트 결과 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    tester = WatchHamsterFunctionTester()
    
    try:
        # 모든 테스트 실행
        results = tester.run_all_tests()
        
        # 결과 저장
        tester.save_results()
        
        # 종료 코드 결정
        if results['overall_status'] in ['excellent', 'good']:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 테스트가 중단되었습니다")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 예외 발생: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()