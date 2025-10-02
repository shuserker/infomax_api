#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POSCO 워치햄스터 모니터링 시스템 테스트

정상 커밋에서 복원한 워치햄스터 모니터링 로직을 테스트합니다.

Requirements: 3.4, 4.2
"""

import unittest
import os
import sys
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from watchhamster_monitor import (
    WatchHamsterMonitor, 
    ProcessStatus, 
    SystemResourceLevel, 
    RecoveryStage
)

class TestWatchHamsterMonitor(unittest.TestCase):
    """워치햄스터 모니터링 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_config = {
            'process_check_interval': 60,  # 테스트용 짧은 간격
            'git_check_interval': 300,
            'status_notification_interval': 600,
            'managed_processes': ['test_process_1', 'test_process_2'],
            'max_restart_attempts': 3,
            'restart_cooldown': 10,
            'webhook_url': 'https://test.webhook.url',
            'bot_profile_image': 'https://test.image.url'
        }
        
        self.monitor = WatchHamsterMonitor(self.test_config)
    
    def test_initialization(self):
        """워치햄스터 모니터링 시스템 초기화 테스트"""
        print("\n🔧 워치햄스터 모니터링 시스템 초기화 테스트")
        
        # 기본 속성 확인
        self.assertIsNotNone(self.monitor.script_dir)
        self.assertIsNotNone(self.monitor.log_file)
        self.assertEqual(self.monitor.process_check_interval, 60)
        self.assertEqual(len(self.monitor.managed_processes), 2)
        
        # 프로세스 상태 추적 초기화 확인
        for process_name in self.monitor.managed_processes:
            self.assertIn(process_name, self.monitor.process_status)
            self.assertEqual(self.monitor.process_status[process_name], ProcessStatus.UNKNOWN)
            self.assertIn(process_name, self.monitor.restart_counts)
            self.assertEqual(self.monitor.restart_counts[process_name], 0)
        
        print("✅ 워치햄스터 모니터링 시스템 초기화 성공")
    
    @patch('psutil.process_iter')
    def test_process_monitoring(self, mock_process_iter):
        """프로세스 감시 알고리즘 테스트"""
        print("\n🔍 프로세스 감시 알고리즘 테스트")
        
        # Mock 프로세스 설정
        mock_proc1 = Mock()
        mock_proc1.info = {
            'pid': 1234,
            'name': 'python',
            'cmdline': ['python', 'test_process_1.py'],
            'create_time': time.time()
        }
        
        mock_proc2 = Mock()
        mock_proc2.info = {
            'pid': 5678,
            'name': 'python', 
            'cmdline': ['python', 'test_process_2.py'],
            'create_time': time.time()
        }
        
        mock_process_iter.return_value = [mock_proc1, mock_proc2]
        
        # 프로세스 모니터링 실행
        results = self.monitor.monitor_processes()
        
        # 결과 검증
        self.assertIsInstance(results, dict)
        self.assertIn('timestamp', results)
        self.assertIn('total_processes', results)
        self.assertIn('healthy_processes', results)
        self.assertIn('process_details', results)
        self.assertIn('system_health', results)
        
        self.assertEqual(results['total_processes'], 2)
        self.assertIn('test_process_1', results['process_details'])
        self.assertIn('test_process_2', results['process_details'])
        
        print(f"📊 프로세스 모니터링 결과: {results['healthy_processes']}/{results['total_processes']} 정상")
        print(f"🏥 시스템 건강도: {results['system_health']}")
        print("✅ 프로세스 감시 알고리즘 테스트 성공")
    
    @patch('subprocess.run')
    def test_git_status_check(self, mock_subprocess):
        """Git 상태 체크 로직 테스트"""
        print("\n📋 Git 상태 체크 로직 테스트")
        
        # Mock Git 명령어 응답 설정
        mock_responses = [
            Mock(returncode=0, stdout='main', stderr=''),  # git branch --show-current
            Mock(returncode=0, stdout='abc12345', stderr=''),  # git rev-parse HEAD
            Mock(returncode=0, stdout='', stderr=''),  # git fetch --dry-run
            Mock(returncode=0, stdout='', stderr='')   # git status --porcelain
        ]
        
        mock_subprocess.side_effect = mock_responses
        
        # Git 상태 체크 실행
        git_status = self.monitor.check_git_status()
        
        # 결과 검증
        self.assertIsInstance(git_status, dict)
        self.assertIn('timestamp', git_status)
        self.assertIn('status', git_status)
        self.assertIn('current_branch', git_status)
        self.assertIn('current_commit', git_status)
        self.assertIn('remote_status', git_status)
        self.assertIn('auto_recovery_possible', git_status)
        
        self.assertEqual(git_status['current_branch'], 'main')
        self.assertEqual(git_status['current_commit'], 'abc12345')
        self.assertEqual(git_status['status'], 'clean')
        
        print(f"🌿 Git 브랜치: {git_status['current_branch']}")
        print(f"📝 현재 커밋: {git_status['current_commit']}")
        print(f"🔍 Git 상태: {git_status['status']}")
        print("✅ Git 상태 체크 로직 테스트 성공")
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_resource_monitoring(self, mock_disk, mock_memory, mock_cpu):
        """시스템 리소스 모니터링 테스트"""
        print("\n📊 시스템 리소스 모니터링 테스트")
        
        # Mock 시스템 리소스 설정
        mock_cpu.return_value = 45.5
        
        mock_memory_obj = Mock()
        mock_memory_obj.percent = 62.3
        mock_memory_obj.available = 4 * 1024**3  # 4GB
        mock_memory.return_value = mock_memory_obj
        
        mock_disk_obj = Mock()
        mock_disk_obj.total = 100 * 1024**3  # 100GB
        mock_disk_obj.used = 70 * 1024**3   # 70GB
        mock_disk_obj.free = 30 * 1024**3   # 30GB
        mock_disk.return_value = mock_disk_obj
        
        # 시스템 리소스 모니터링 실행
        resource_status = self.monitor.monitor_system_resources()
        
        # 결과 검증
        self.assertIsInstance(resource_status, dict)
        self.assertIn('timestamp', resource_status)
        self.assertIn('cpu', resource_status)
        self.assertIn('memory', resource_status)
        self.assertIn('disk', resource_status)
        self.assertIn('overall_level', resource_status)
        
        self.assertEqual(resource_status['cpu']['percent'], 45.5)
        self.assertEqual(resource_status['memory']['percent'], 62.3)
        self.assertEqual(resource_status['overall_level'], SystemResourceLevel.NORMAL)
        
        print(f"💻 CPU 사용률: {resource_status['cpu']['percent']:.1f}%")
        print(f"🧠 메모리 사용률: {resource_status['memory']['percent']:.1f}%")
        print(f"💾 디스크 사용률: {resource_status['disk']['percent']:.1f}%")
        print(f"🏥 전체 상태: {resource_status['overall_level']}")
        print("✅ 시스템 리소스 모니터링 테스트 성공")
    
    def test_dynamic_alert_message_generation(self):
        """동적 알림 메시지 생성 테스트"""
        print("\n📝 동적 알림 메시지 생성 테스트")
        
        # 테스트 데이터 설정
        process_results = {
            'healthy_processes': 1,
            'total_processes': 2,
            'failed_processes': ['test_process_2'],
            'system_health': 'warning'
        }
        
        git_status = {
            'status': 'clean',
            'current_branch': 'main',
            'current_commit': 'abc12345'
        }
        
        resource_status = {
            'overall_level': SystemResourceLevel.WARNING,
            'cpu': {'percent': 75.0},
            'memory': {'percent': 80.0},
            'disk': {'percent': 85.0},
            'warnings': ['CPU 사용률 주의: 75.0%']
        }
        
        # 다양한 알림 타입 테스트
        alert_types = ['status', 'error', 'recovery', 'critical']
        
        for alert_type in alert_types:
            message = self.monitor.generate_dynamic_alert_message(
                process_results, git_status, resource_status, alert_type
            )
            
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
            self.assertIn('POSCO 워치햄스터', message)
            self.assertIn(datetime.now().strftime('%Y-%m-%d'), message)
            
            print(f"📨 {alert_type} 알림 메시지 생성 성공 ({len(message)} 문자)")
        
        print("✅ 동적 알림 메시지 생성 테스트 성공")
    
    @patch('subprocess.Popen')
    def test_process_lifecycle_management(self, mock_popen):
        """프로세스 생명주기 관리 테스트"""
        print("\n🔄 프로세스 생명주기 관리 테스트")
        
        # Mock 프로세스 설정
        mock_process = Mock()
        mock_process.pid = 9999
        mock_process.poll.return_value = None  # 실행 중
        mock_popen.return_value = mock_process
        
        # 프로세스 시작 테스트
        result = self.monitor.manage_process_lifecycle('test_process_1', 'start')
        
        self.assertIsInstance(result, dict)
        self.assertIn('timestamp', result)
        self.assertIn('process_name', result)
        self.assertIn('action', result)
        self.assertIn('success', result)
        self.assertIn('details', result)
        
        self.assertEqual(result['process_name'], 'test_process_1')
        self.assertEqual(result['action'], 'start')
        
        print(f"🚀 프로세스 시작 테스트: {result['action']} - {'성공' if result['success'] else '실패'}")
        print(f"📋 세부사항: {len(result['details'])}개 항목")
        print("✅ 프로세스 생명주기 관리 테스트 성공")
    
    def test_auto_recovery_scenario(self):
        """자동 복구 시나리오 테스트"""
        print("\n🚀 자동 복구 시나리오 테스트")
        
        # 문제 상황 시뮬레이션
        process_results = {
            'healthy_processes': 0,
            'total_processes': 2,
            'failed_processes': ['test_process_1', 'test_process_2'],
            'system_health': 'critical'
        }
        
        git_status = {
            'status': 'modified',
            'auto_recovery_possible': True,
            'errors': []
        }
        
        resource_status = {
            'overall_level': SystemResourceLevel.CRITICAL,
            'critical_issues': ['메모리 사용률 높음: 90.0%']
        }
        
        # 자동 복구 시나리오 실행
        with patch.object(self.monitor, 'manage_process_lifecycle') as mock_lifecycle:
            mock_lifecycle.return_value = {
                'success': True,
                'details': ['프로세스 복구 성공']
            }
            
            recovery_result = self.monitor.execute_auto_recovery_scenario(
                process_results, git_status, resource_status
            )
        
        # 결과 검증
        self.assertIsInstance(recovery_result, dict)
        self.assertIn('timestamp', recovery_result)
        self.assertIn('total_issues', recovery_result)
        self.assertIn('recovery_attempts', recovery_result)
        self.assertIn('successful_recoveries', recovery_result)
        self.assertIn('final_status', recovery_result)
        
        print(f"🔍 감지된 문제: {recovery_result['total_issues']}개")
        print(f"🔧 복구 시도: {recovery_result['recovery_attempts']}회")
        print(f"✅ 성공한 복구: {recovery_result['successful_recoveries']}개")
        print(f"🏁 최종 상태: {recovery_result['final_status']}")
        print("✅ 자동 복구 시나리오 테스트 성공")
    
    def test_monitoring_status(self):
        """모니터링 상태 조회 테스트"""
        print("\n📊 모니터링 상태 조회 테스트")
        
        status = self.monitor.get_monitoring_status()
        
        # 결과 검증
        self.assertIsInstance(status, dict)
        self.assertIn('timestamp', status)
        self.assertIn('system_start_time', status)
        self.assertIn('managed_processes', status)
        self.assertIn('process_status', status)
        self.assertIn('configuration', status)
        
        self.assertEqual(len(status['managed_processes']), 2)
        self.assertIn('process_check_interval', status['configuration'])
        
        print(f"⏱️ 시스템 시작 시간: {status['system_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 관리 프로세스: {len(status['managed_processes'])}개")
        print(f"⚙️ 체크 간격: {status['configuration']['process_check_interval']}초")
        print("✅ 모니터링 상태 조회 테스트 성공")

def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🐹 POSCO 워치햄스터 모니터링 시스템 종합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestWatchHamsterMonitor)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("🏁 워치햄스터 모니터링 시스템 테스트 완료")
    
    # 결과 요약
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 테스트 결과 요약:")
    print(f"  • 총 테스트: {total_tests}개")
    print(f"  • 성공: {total_tests - failures - errors}개")
    print(f"  • 실패: {failures}개")
    print(f"  • 오류: {errors}개")
    print(f"  • 성공률: {success_rate:.1f}%")
    
    if failures == 0 and errors == 0:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("✅ 워치햄스터 모니터링 로직이 정상적으로 복원되었습니다.")
    else:
        print(f"\n⚠️ {failures + errors}개의 테스트에서 문제가 발생했습니다.")
        
        if result.failures:
            print("\n❌ 실패한 테스트:")
            for test, traceback in result.failures:
                print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n💥 오류가 발생한 테스트:")
            for test, traceback in result.errors:
                print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result

if __name__ == "__main__":
    run_comprehensive_test()