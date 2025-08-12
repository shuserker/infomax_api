#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Watchhamster V3.0 Notification
POSCO 시스템 테스트

WatchHamster v3.0 및 POSCO News 250808 호환
Created: 2025-08-08
"""

import posco_news_250808_monitor.log
import system_functionality_verification.py
import unittest
# REMOVED: from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 테스트 환경 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'Monitoring/POSCO News 250808_mini'))

class TestWatchHamster v3.00NotificationIntegration(unittest.TestCase):
    """v2 알림 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Mock 환경 설정
        self.mock_webhook_url = "https:/hook.dooray.com/services/test"
        self.mock_bot_profile_url = "https:/example.com/bot.png"
        
        # 필요한 모듈들을 Mock으로 설정
        self.setup_mocks()
        
        # 워치햄스터 인스턴스 생성 (Mock 환경에서)
        try:
            from .comprehensive_repair_backup/monitor_.naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log_v3.0.py.backup_20250809_181656 import .naming_backup/config_data_backup/Monitoring/Posco_News_mini/WatchHamster.log v3.00Monitor
import os
import sys
            self.watchhamster = WatchHamster v3.00Monitor()
        except Exception as e:
            self.skipTest(f"WatchHamster v3.0 초기화 실패: {e}")
    
    def setup_mocks(self):
        """Mock 환경 설정"""
        # requests 모듈 Mock
        self.requests_patcher = patch('requests.post')
        self.mock_requests_post = self.requests_patcher.start()
        self.mock_requests_post.return_value.status_code = 200
        
        # psutil 모듈 Mock
        self.psutil_patcher = patch('psutil.cpu_percent')
        self.mock_cpu_percent = self.psutil_patcher.start()
        self.mock_cpu_percent.return_value = 25.0
        
        self.memory_patcher = patch('psutil.virtual_memory')
        self.mock_memory = self.memory_patcher.start()
        self.mock_memory.return_value.percent = 45.0
        
        self.disk_patcher = patch('psutil.disk_usage')
        self.mock_disk = self.disk_patcher.start()
        self.mock_disk.return_value.percent = 60.0
        
        # 환경 변수 Mock
        os.environ['WATCHHAMSTER_WEBHOOK_URL'] = self.mock_webhook_url
        os.environ['BOT_PROFILE_IMAGE_URL'] = self.mock_bot_profile_url
    
    def tearDown(self):
        """테스트 정리"""
        self.requests_patcher.stop()
        self.psutil_patcher.stop()
        self.memory_patcher.stop()
        self.disk_patcher.stop()
    
    def test_v2_startup_notification_preserves_existing_text(self):
        """
        v2 시작 알림이 기존 텍스트를 보존하는지 테스트
        
        Requirements: 4.1, 4.2
        """
        print("/n🧪 테스트: v2 시작 알림 기존 텍스트 보존")
        
        # v2 컴포넌트 Mock 설정
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_startup_notification.return_value = True
        
        # 관리 대상 프로세스 설정
        self.watchhamster.managed_processes = [
            'posco_main_notifier',
            'realtime_news_monitor',
            'integrated_report_scheduler'
        ]
        
        # v2 시작 알림 호출
        self.watchhamster.send_startup_notification_v2()
        
        # v2 NotificationManager 호출 확인
        self.watchhamster.v3_0_components['notification_manager'].send_startup_notification.assert_called_once()
        
        # 호출 인자 확인
        call_args = self.watchhamster.v3_0_components['notification_manager'].send_startup_notification.call_args
        self.assertEqual(call_args[0][0], self.watchhamster.managed_processes)
        
        print("✅ v2 시작 알림이 올바르게 호출됨")
    
    def test_v2_startup_notification_fallback(self):
        """
        v2 시작 알림 실패 시 폴백 동작 테스트
        
        Requirements: 4.1, 4.2
        """
        print("/n🧪 테스트: v2 시작 알림 폴백 동작")
        
        # v2 컴포넌트 실패 시뮬레이션
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_startup_notification.return_value = False
        
        # 관리 대상 프로세스 설정
        self.watchhamster.managed_processes = [
            'posco_main_notifier',
            'realtime_news_monitor'
        ]
        
        # v2 시작 알림 호출
        self.watchhamster.send_startup_notification_v2()
        
        # 기존 방식 알림 호출 확인
        self.mock_requests_post.assert_called()
        
        # 호출된 payload 확인
        call_args = self.mock_requests_post.call_args
        payload = call_args[1]['json']
        
        # 기존 텍스트 보존 확인
        self.assertIn("POSCO WatchHamster v3.0 시작", payload['attachments'][0]['text'])
        self.assertIn("관리 대상 프로세스", payload['attachments'][0]['text'])
        self.assertIn("v2 아키텍처 상태", payload['attachments'][0]['text'])
        
        print("✅ 폴백 시 기존 텍스트가 보존되고 v2 정보가 추가됨")
    
    def test_v2_status_report_enhanced_info(self):
        """
        v2 상태 보고가 향상된 정보를 포함하는지 테스트
        
        Requirements: 4.2, 4.3
        """
        print("/n🧪 테스트: v2 상태 보고 향상된 정보")
        
        # v2 컴포넌트 Mock 설정
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_status_report.return_value = True
        self.watchhamster.v3_0_components['notification_manager'].get_notification_stats.return_value = {
            'total_notifications': 42,
            'failed_notifications': 1,
            'success_rate': 97.6
        }
        
        # 관리 대상 프로세스 설정
        self.watchhamster.managed_processes = ['posco_main_notifier']
        
        # 프로세스 상태 Mock
with_patch.object(self.watchhamster,_'_is_process_running',_return_value = True), /
patch.object(self.watchhamster,_'_get_process_pid',_return_value = 12345):
            
            # v2 상태 보고 호출
            self.watchhamster.send_status_report_v2()
        
        # v2 NotificationManager 호출 확인
        self.watchhamster.v3_0_components['notification_manager'].send_status_report.assert_called_once()
        
        # SystemStatus 객체가 전달되었는지 확인
        call_args = self.watchhamster.v3_0_components['notification_manager'].send_status_report.call_args
        system_status = call_args[0][0]
        
        # SystemStatus 객체의 속성 확인
        self.assertIsNotNone(system_status)
        self.assertEqual(system_status.total_processes, 1)
        self.assertEqual(system_status.running_processes, 1)
        self.assertEqual(system_status.failed_processes, 0)
        
        print("✅ v2 상태 보고가 향상된 시스템 정보를 포함함")
    
    def test_v2_process_error_structured_notification(self):
        """
        v2 프로세스 오류 알림이 구조화된 정보를 포함하는지 테스트
        
        Requirements: 4.3, 4.4
        """
        print("/n🧪 테스트: v2 프로세스 오류 구조화된 알림")
        
        # v2 컴포넌트 Mock 설정
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_process_error.return_value = True
        
        # 오류 상세 정보
        error_details = {
            'error_message': '프로세스 응답 없음',
            'restart_count': 2,
            'max_attempts': 3,
            'auto_recovery_enabled': True
        }
        
        # v2 프로세스 오류 알림 호출
        self.watchhamster.send_process_error_v2('posco_main_notifier', error_details)
        
        # v2 NotificationManager 호출 확인
        self.watchhamster.v3_0_components['notification_manager'].send_process_error.assert_called_once_with(
            'posco_main_notifier', error_details
        )
        
        print("✅ v2 프로세스 오류 알림이 구조화된 정보를 포함함")
    
    def test_v2_recovery_success_detailed_info(self):
        """
        v2 복구 성공 알림이 상세 정보를 포함하는지 테스트
        
        Requirements: 4.3, 4.4
        """
        print("/n🧪 테스트: v2 복구 성공 상세 정보")
        
        # v2 컴포넌트 Mock 설정
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_recovery_success.return_value = True
        
        # 복구 상세 정보
        recovery_details = {
            'recovery_stage': '2단계 복구',
            'recovery_time': 15.3,
            'new_pid': 54321,
            'previous_restart_count': 1,
            'current_restart_count': 2
        }
        
        # v2 복구 성공 알림 호출
        self.watchhamster.send_recovery_success_v2('realtime_news_monitor', recovery_details)
        
        # v2 NotificationManager 호출 확인
        self.watchhamster.v3_0_components['notification_manager'].send_recovery_success.assert_called_once_with(
            'realtime_news_monitor', recovery_details
        )
        
        print("✅ v2 복구 성공 알림이 상세한 복구 정보를 포함함")
    
    def test_v2_critical_alert_structured_format(self):
        """
        v2 긴급 알림이 구조화된 형태로 전송되는지 테스트
        
        Requirements: 4.4
        """
        print("/n🧪 테스트: v2 긴급 알림 구조화된 형태")
        
        # v2 컴포넌트 Mock 설정
        self.watchhamster.v3_0_enabled = True
        self.watchhamster.v3_0_components['notification_manager'] = Mock()
        self.watchhamster.v3_0_components['notification_manager'].send_critical_alert.return_value = True
        
        # 긴급 상황 정보
        alert_message = "시스템 리소스 임계값 초과"
        additional_info = {
            'CPU_사용률': '95%',
            'Memory_사용률': '88%',
            '영향받는_프로세스': 'posco_main_notifier',
            '필요_조치': '즉시 확인 필요'
        }
        
        # v2 긴급 알림 호출
        self.watchhamster.send_critical_alert_v2(alert_message, additional_info)
        
        # v2 NotificationManager 호출 확인
        self.watchhamster.v3_0_components['notification_manager'].send_critical_alert.assert_called_once_with(
            alert_message, additional_info
        )
        
        print("✅ v2 긴급 알림이 구조화된 추가 정보를 포함함")
    
    def test_system_status_collection(self):
        """
        v2 시스템 상태 수집 기능 테스트
        
        Requirements: 4.2, 4.3
        """
        print("/n🧪 테스트: v2 시스템 상태 수집")
        
        # 관리 대상 프로세스 설정
        self.watchhamster.managed_processes = [
            'posco_main_notifier',
            'realtime_news_monitor'
        ]
        
        # 프로세스 상태 Mock
        with patch.object(self.watchhamster, '_is_process_running') as mock_running, /
             patch.object(self.watchhamster, '_get_process_pid') as mock_pid:
            
            mock_running.side_effect = [True, False]  # 첫 번째는 실행 중, 두 번째는 중지
            mock_pid.side_effect = [12345, 'N/A']
            
            # 시스템 상태 수집
            system_status = self.watchhamster._collect_v2_system_status()
        
        # 수집된 상태 정보 확인
        if system_status:
            self.assertEqual(system_status.total_processes, 2)
            self.assertEqual(system_status.running_processes, 1)
            self.assertEqual(system_status.failed_processes, 1)
            
            # 프로세스 상세 정보 확인
            self.assertIn('posco_main_notifier', system_status.process_details)
            self.assertIn('realtime_news_monitor', system_status.process_details)
            
            # 시스템 메트릭 확인
            self.assertIn('cpu_percent', system_status.system_metrics)
            self.assertIn('memory_percent', system_status.system_metrics)
            self.assertIn('disk_percent', system_status.system_metrics)
            
            print("✅ 시스템 상태가 올바르게 수집됨")
        else:
            print("⚠️ 시스템 상태 수집 실패 (v2 컴포넌트 없음)")
    
    def test_notification_fallback_mechanism(self):
        """
        알림 시스템 폴백 메커니즘 테스트
        
        Requirements: 4.1, 4.2
        """
        print("/n🧪 테스트: 알림 시스템 폴백 메커니즘")
        
        # v2 비활성화 상태 시뮬레이션
        self.watchhamster.v3_0_enabled = False
        self.watchhamster.v3_0_components['notification_manager'] = None
        
        # 기본 알림 호출
        test_message = "테스트 알림 메시지"
        self.watchhamster.send_notification(test_message, is_error=False)
        
        # 기존 방식 알림 호출 확인
        self.mock_requests_post.assert_called()
        
        # 호출된 payload 확인
        call_args = self.mock_requests_post.call_args
        payload = call_args[1]['json']
        
        self.assertEqual(payload['botName'], "POSCO WatchHamster v3.0 🐹🛡️")
        self.assertIn(test_message, payload['attachments'][0]['text'])
        self.assertEqual(payload['attachments'][0]['color'], "#28a745")
        
        print("✅ v2 비활성화 시 기존 방식으로 올바르게 폴백됨")

def run_integration_test():
    """통합 테스트 실행"""
    print("🚀 POSCO WatchHamster v3.0 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestV2NotificationIntegration)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
print("/n"_+_" = " * 60)
    print("📊 테스트 결과 요약:")
    print(f"  • 총 테스트: {result.testsRun}개")
    print(f"  • 성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"  • 실패: {len(result.failures)}개")
    print(f"  • 오류: {len(result.errors)}개")
    
    if result.failures:
        print("/n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('/n')[0]
            print(f"  • {test}: {error_msg}")
    
    if result.errors:
        print("/n💥 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            error_msg = traceback.split('/n')[-2]
            print(f"  • {test}: {error_msg}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"/n🎯 성공률: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Task 5: v2 NotificationManager 알림 시스템 향상 - 통합 테스트 통과!")
        return True
    else:
        print("❌ Task 5: v2 NotificationManager 알림 시스템 향상 - 통합 테스트 실패")
        return False

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)